#! /usr/bin/env ruby

require 'open-uri'
#require 'json'
require 'nokogiri'

# appID is required by trimet
@appID = "091253C02A8A508C8B7B9779E"

# The trimet arrivals v1 web service
@uri_base = "https://developer.trimet.org/ws/V1/arrivals/locIDs/"

# stop IDs:
# 8333 (Library/SW 9th, for Red/Blue)
# 7787 (SW 6th & Pine, for Green)
# 7782 (SW 6th & Oak, for 12)
# 8402 (NW Everett & Park, for 77)
@stop_list  = [8333, 7787, 7782, 8402]

# stop IDs can be comma-separated list (up to 10)
# ie, 8333,7787,7782,8402 for all four of the stops close to work
# Green line is route 200
# Red line is route 90
# Blue line is route 100
# bus routes are their respective numbers (12, 77)
@route_list = [12, 77, 90, 100, 200]


def get_arrivals 
  arrivals_url = @uri_base + @stop_list.join(",") + "/appID/#{@appID}"
  begin
    doc = Nokogiri::XML(open(arrivals_url))
    return doc
  rescue OpenURI::HTTPError
    abort "No network connection?"
  end
end


def convert_time(time_in)
 return Time.at(time_in/1000).to_datetime
end


# main
arrivals_info = get_arrivals
prefix = 'urn:trimet:arrivals'
fp = './/' + prefix

namespaces = arrivals_info.collect_namespaces

arrivals_info.xpath('.//location', namespaces).each do |node|
  if @stop_list.include?node.attr('locid')
    puts "#{node.attr('locid')} is in stop_list"
    stop_location = node.attr('desc')
    stop_direction = node.attr('dir')
  end

  puts "The next arrivals due at our stops (#{@stop_list.join(',')}) are: "

  isabus = false;

  arrivals_info.xpath('.//arrival', namespaces).each do |arrival|
    if @route_list.include?arrival.attr('route')
      print arrival.attr('fullSign')
      if arrival.attr('status') == 'estimated'
        print 'Estimated arrival time: ' + conv_time(int(arrival.attr['estimated']))
        isabus = true
      end
    end
  end

end
