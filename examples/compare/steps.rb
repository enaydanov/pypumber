Given /^I'm a cucumber$/ do
#   puts '.'
#   @runs ||= 0
#   @runs += 1
#   if @runs > 1
      puts '.'
      pending
#   end
end

Given /^passing$/ do
  puts '.'
end

Given /^failing$/ do
  1 / 0
end

Before do
  puts :before
end

After do
  puts :after
end
