require 'json'
require 'uri'
require 'net/http'
require 'hue'

class BusLight
  Version = '0.0.1'

  # See https://developer.trimet.org/ws_docs/arrivals_ws.shtml
  # TRIMET_V1_STOPS_URL = "https://developer.trimet.org/ws/V1/arrivals"
  # See https://developer.trimet.org/ws_docs/arrivals2_ws.shtml
  TRIMET_STOPS_URL = "https://developer.trimet.org/ws/v2/arrivals"
  TRIMET_API_KEY = "091253C02A8A508C8B7B9779E"
  STOP_ID= "1818"

  def initialize(arguments, stdin)
    @Client = Hue::Client.new
  end

  def run
    # Get upcoming arrivals
    uri = URI.parse( "#{TRIMET_STOPS_URL}?appID=#{TRIMET_API_KEY}&json=true&locIDs=#{STOP_ID}" )
    puts uri
    response = Net::HTTP.get_response(uri)
    puts response.body
    trimet_response = JSON.parse(response.body)
    scheduled = trimet_response['resultSet']['arrival'][0]['scheduled']
    estimated = trimet_response['resultSet']['arrival'][0]['estimated']
    current = Time.new
    if (scheduled - 600000 < time.strftime('%s').to_i * 1000) || (estimated - 600000 < time.strftime('%s').to_i * 1000)
      puts "bus is arriving within ten minutes"
      Client.lights[3].on!
    end 

  end

end # end of class

app = BusLight.new(ARGV, STDIN)
app.run
