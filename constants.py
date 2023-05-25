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

# Used to verify image analysis. If the graph has a number of intervals that
# isn't in this list, the parser may have analysed it wrongly.
# Also maps how many bars there are for each number of intervals
# Note: 11 intervals can also mean 101 bars, but we ignore those
# Note: because ZERO exists, must add 1 to both number of intervals and number of bars
NUMBER_OF_INTERVALS = {6: 26, 11: 51, 16: 76}


# Subjects which are math or science (i.e. have internals/externals of 50 marks)
MATH_SCIENCE_SUBJECTS = [
    "ag_science",
    "biology",
    "chemistry",
    "earth_science",
    "marine_science",
    "maths_general",
    "maths_methods",
    "maths_specialist",
    "physics",
    "psychology"
]


# The number of marks in the internals/externals in a subject
# Based on whether it is a math/science subject
NUMBER_OF_MARKS = {
    True: {     # math/science subjects
        "Internals": 50,
        "Externals": 50
    },
    False: {    # non-math/science subjects
        "Internals": 75,
        "Externals": 25
    }
}
