#! /usr/bin/env ruby

require 'json'

file = File.read('/Users/jacob.vigeveno/location-output.json')
data_hash = JSON.parse(file)

points = Array.new
data_hash.map {|point|
  if point['lat'] && point['lon']
    obj = {:type => "Feature", 
           :properties => {}, 
           :geometry => {
             :type => "Point",
             :coordinates =>[point['lon'].to_f, 
                             point['lat'].to_f] 
           } 
    }
    points.push(obj)
  end
}
geohash = { :type => "FeatureCollection" }
geohash[:features] = points
#puts JSON.pretty_generate(geohash)
puts geohash.to_json

