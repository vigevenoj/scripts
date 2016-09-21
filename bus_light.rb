require 'hue'
require 'json'
require 'net/http'
require 'rufus-scheduler'
require 'uri'
require 'yaml'

##
# Integration between next Trimet arrival and an indicator light
#
# Requires a configuration file named .bus_light.yaml in the same directory,
# which contains the following items:
# trimet: a hash containing these elements
#  api_key : a Trimet API key
#  stopIDs : an array of Trimet stop IDs
class BusLight
  Version = '0.0.1'

  # See https://developer.trimet.org/ws_docs/arrivals_ws.shtml
  # TRIMET_V1_STOPS_URL = "https://developer.trimet.org/ws/V1/arrivals"
  # See https://developer.trimet.org/ws_docs/arrivals2_ws.shtml
  TRIMET_STOPS_URL = "https://developer.trimet.org/ws/v2/arrivals"

  def initialize(arguments, stdin)
    configuration = YAML.load_file(File.join(__dir__, '.bus_light.yaml'))
    @trimet_api_key = configuration['trimet']['api_key']
    @trimet_stops = configuration['trimet']['stopIDs']
    @Client = Hue::Client.new
    @light = @Client.lights[3]
  end

  ##
  # Schedule the next time we should check for a bus
  def schedule_next_check time_to_check
    # Start checking at 6:55 AM PDT for buses.
    # If a bus is scheduled or estimated to arrive within the next 10 minutes, check again in 60 seconds
    # If a bus is not scheduled or estimated to arrive within 15 minutes
    #   Determine how far out the next bus is and check 15 minutes prior to estimate/schedule
  end
  
  ##
  # Check for a bus
  #
  def check_for_bus
    uri = URI.parse( "#{TRIMET_STOPS_URL}?json=true&appID=#{@trimet_api_key}&locIDs=#{@trimet_stops.join(',')}" )
    response = Net::HTTP.get_response(uri)
    trimet_response =JSON.parse(response.body)
    
    next_arrival = trimet_response['resultSet']['arrival'][0]
    scheduled = next_arrival['scheduled']
    estimated = next_arrival['estimated']

    soonest = [scheduled,estimated].compact.min
    now = DateTime.now.strftime("%Q")
    puts "next bus at #{DateTime.strptime(soonest.to_s, '%Q')}"
    puts "bus is #{(soonest.to_i - now.to_i)/1000} seconds away"


    unless (soonest - now.to_i) <= 0
      update_color ( soonest - now.to_i)
    end

  end

  ##
  # Update the lamp color based on the +BigNum+ milliseconds until the next bus arrival
  #
  # An ArgumentError is raised if the difference is negative or zero
  def update_color soonest_bus
    if soonest_bus < 0
      raise ArgumentError.new('Soonest bus cannot be in zero or negative milliseconds')
    end
    if (soonest_bus >= 15 * 60 * 1000) # if >= 15 minutes away, light off
      @light.off!
      puts "Off. no bus for at least fifteen minutes"
      schedule_next_check(Time.now + (5*60))
    elsif (soonest_bus >= 10 * 60 * 1000 && soonest_bus < 15 * 60 * 1000) # 10-15 minutes away
      @light.set_state( { :on => true, :xy => [0.4317,0.4996], :alert => "select" }, 50 ) # "yellow"
      @light.on!
      puts "yellow"
      schedule_next_check(Time.now + 60)
    elsif (soonest_bus >= 9 * 60 * 1000 && soonest_bus < 10 * 60 * 1000) # 9-10 minutes away
      @light.set_state( { :on => true, :xy => [0.46 , 0.4], :alert => "select" }, 50 ) # "gold"
      puts "gold"
      schedule_next_check(Time.now + 60)
    elsif (soonest_bus >= 7 * 60 * 1000 && soonest_bus < 9 * 60 * 1000) # 7-9 minutes away
      @light.set_state( { :on => true, :xy => [0.5113,0.4413] }, 50 ) # "goldenrod"
      puts "goldenrod"
      schedule_next_check(Time.now + 60)
    elsif (soonest_bus >= 5 * 60 * 1000 && soonest_bus < 7 * 60 * 1000 ) # 5-7 minutes away
      @light.set_state( { :on => true, :xy => [0.5916,0.3824] }, 50 ) # "dark orange"
      puts "dark orange"
      schedule_next_check(Time.now + 60)
    elsif (soonest_bus >= 4 * 60 * 1000 && soonest_bus < 5 * 60 * 1000) # 4-5 minutes away
      @light.set_state( { :on => true, :xy => [0.5562,0.4084], :alert => "select" }, 50 ) # "orange"
      puts "orange"
      schedule_next_check(Time.now + 60)
    elsif (soonest_bus >= 3 * 60 * 1000 && soonest_bus < 4 * 60 * 1000) # 3-4 minutes away
      @light.set_state( { :on => true, :xy => [0.6733,0.3224], :alert => "select" }, 50 ) # "orange red" 
      puts "orange red"
      schedule_next_check(Time.now + 60)
    elsif (soonest_bus < 3 * 60 * 1000) # less than 3 minutes away
      @light.set_state( { :on => true, :xy => [0.674,0.322] }, 50) # "red"
      puts "red"
      schedule_next_check(Time.now + 60)
    end
  end

  def run
    # Get upcoming arrivals
    trimet_response = check_for_bus

  end

end # end of class

if __FILE__ == $0 then
  app = BusLight.new(ARGV, STDIN)
  app.run
end
