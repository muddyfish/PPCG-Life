require 'json'

class Range
  def product range2
    self.to_a.product range2.to_a
  end
end

args = JSON.parse(ARGV[0])
bot_id = args["bot_id"]
width  = args["x_size"]
height = args["y_size"]
board  = args["board"]

generator = [[2,2], [2,3], [2,6], [3,2], [3,5], [4,2], [4,5], [4,6], [5,4], [6,2], [6,4], [6,5], [6,6]]

targets = []

iterations = 50
gen_location = nil
while !gen_location && iterations > 0
  y = rand height - 9
  x = rand width  - 9
  temp = (0...9).product(0...9).map{|_y, _x| [y + _y, x + _x]}
  if temp.all?{|_y,_x| !board["(#{y},#{x})"]}
    gen_location = temp
    targets += generator.map{|_y, _x| [y + _y, x + _x]}
  end

  iterations -= 1
end

enemies = board.keys.reject {|k| board[k] == bot_id}
interrupts = []
enemies.each do |location|
  y, x = location.scan(/\d+/).map &:to_i
  interrupts |= ((y-1)..(y+1)).product((x-1)..(x+1)).reject{|y, x| gen_location.include?([y,x]) || board["(#{y},#{x})"]}
end

targets += interrupts.sample(30 - targets.size)

puts JSON.dump(targets)
