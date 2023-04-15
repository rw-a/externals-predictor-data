IMAGES_DIRECTORY = {
    2020: {
        "Internals": 6,          # this means that the internals results are always on page 6 of the subject report
        "Externals": 9,
    },                           # totals doesn't exist in 2020 subject reports
    2021: {
        "Internals": 5,
        "Externals": 9,
        "Total": 10              # internals + externals total (out of 100)
    },
    2022: {
        "Internals": 5,
        "Externals": 9,
        "Total": 9
    }
}

# how much raw score each interval gap represents
AXIS_INTERVAL_DISTANCE = {
    "Internals": 5,
    "Externals": 5,
    "Total": 10
}

# used to verify image analysis. if the graph has a number of intervals that isn't in this list, it read it wrong
# also maps how many bars there are for each number of intervals
# note: 11 intervals can also mean 101 bars but we ignore those
# note: because ZERO exists, must add 1 to both number of intervals and number of bars
NUMBER_OF_INTERVALS = {6: 26, 11: 51, 16: 76}
