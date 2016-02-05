#
# Script uses owntracks location data and the Trimet API to provide
# instructions on how to get home from current location.
#
# Configuration file should be named .bus_me_home.yaml in the same directory
# as this script.
# Required configuration elements are 
# * mqtt broker
# ** host
# ** port
# ** ssl?
# ** ca_cert? 
# ** username
# ** password
# * a valid Trimet App ID
# * an array containing a latitude, and a longitude
#
# Author:: Jacob Vigeveno
# Copyright:: Copyright (c) 2016
# License:: MIT license, same as all the things it uses
#
require 'mqtt'
require 'json'
require 'net/http'
require 'uri'
require 'nokogiri'
require 'yaml'
require 'bigdecimal'

class BusMeHome
  Version = '0.0.1'

  @@trimet_stops_url = "https://developer.trimet.org/ws/V1/stops"
  @@trimet_planner_url = "https://developer.trimet.org/ws/V1/trips/tripplanner"

  def initialize(arguments, stdin)
    configuration = YAML.load_file(File.join(__dir__, '.bus_me_home.yaml'))

    @client = MQTT::Client.new
    @client.host = configuration['mqtt']['host']
    @client.port = configuration['mqtt']['port']
    @client.ssl = configuration['mqtt']['ssl']
    @client.ca_file = configuration['mqtt']['ca_cert']
    @client.username = configuration['mqtt']['username']
    @client.password = configuration['mqtt']['password']

    # an api key for trimet
    @trimet_api_key = configuration['trimet']['appID'] 

    # Home location
    @home = configuration['home']


    STDOUT.sync = true
    @log = Logger.new(STDOUT)
    #log = Logger.new('busmehome.log', 10, 1048576)
    @log.level = Logger::INFO
  end

  # Distance function from 
  # http://stackoverflow.com/questions/12966638/how-to-calculate-the-distance-between-two-gps-coordinates-without-using-google-m
  def distance(loc1, loc2)
    rad_per_deg = Math::PI/180  # PI / 180
    rkm = 6371                  # Earth radius in kilometers
    rm = rkm * 1000             # Radius in meters

    dlat_rad = (loc2[0]-loc1[0]) * rad_per_deg  # Delta, converted to rad
    dlon_rad = (loc2[1]-loc1[1]) * rad_per_deg

    lat1_rad, lon1_rad = loc1.map {|i| i * rad_per_deg }
    lat2_rad, lon2_rad = loc2.map {|i| i * rad_per_deg }

    a = Math.sin(dlat_rad/2)**2 + Math.cos(lat1_rad) * Math.cos(lat2_rad) * Math.sin(dlon_rad/2)**2
    c = 2 * Math::atan2(Math::sqrt(a), Math::sqrt(1-a))

    rm * c # Delta in meters
  end

  # Parse the trimet response and output simple instructions
  def do_some_stuff_with_trimet_response trimet
   xml = Nokogiri::XML(trimet)
   xml.xpath("//xmlns:itinerary").each do |itinerary|
     puts "itinerary #{itinerary["id"]}"
     legs = itinerary.xpath("xmlns:leg")
     legs.each do |leg|
       if leg == legs.last 
         break 
       end
       transitMode = leg.attribute('mode').text
       routeName = leg.xpath("xmlns:route/xmlns:name").text.strip
       stopDescription = leg.xpath("xmlns:to/xmlns:description").text.strip
       if transitMode.eql?("Walk") 
         puts "#{transitMode} to #{stopDescription}"
       else 
         puts "#{transitMode} #{routeName} to #{stopDescription}"
       end
     end
   end
  end

  # To be implemented later
  def get_nearby_stops(lat, lon)
    # hit trimet api for stops near this location
    # https://developer.trimet.org/ws/V1/stops
  end

  # Look up phone's current location, ask trimet how to get home.
  def get_me_home(lat, lon)
    # hit trimet trip planner to get home
    # https://developer.trimet.org/ws/V1/trips/tripplanner
    fromCoord = "#{lon},#{lat}"
    toCoord = "#{@home[1]},#{@home[0]}"
    uri = URI.parse( "#{@@trimet_planner_url}?fromCoord=#{fromCoord}&toCoord=#{toCoord}&min=X&appID=#{@trimet_api_key}" )
    response = Net::HTTP.get_response(uri)
    do_some_stuff_with_trimet_response response.body
  end

  def parse_location_update(message)
    begin
      parsed = JSON.parse(message)
      if(parsed["_type"] == "location")
        @latitude = BigDecimal( parsed["lat"] )
        @longitude = BigDecimal( parsed["lon"] )
      end
    rescue JSON::ParserError => e
      # message is invalid json
    end
  end

  def run
    @client.connect()
    topic,message = @client.get('owntracks/#')

    begin
      parse_location_update(message)
      @log.info(sprintf("At %.2f, %.2f", @latitude, @longitude))
      remoteness = distance( [@latitude, @longitude], @home) 
      @log.info("#{remoteness} meters from home on a perfect sphere...")
      if remoteness > 500
        get_me_home(@latitude, @longitude)
      else
        puts "Walk home"
      end

    rescue Exception => e
      puts e.message
      puts e.backtrace.inspect
    end

    @client.disconnect()
  end

end

app = BusMeHome.new(ARGV, STDIN)
app.run
