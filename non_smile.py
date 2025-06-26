import numpy as np

# If we would not use SMILE, but instead of that an open source library, what would be a wise choice?
# There are (at least) two contenders: pgmpy and pomegranate.
# pgmpy is a more recent development with a lot of features.
# pomegranate is older with less active development at it seems.

# The code is this file is a preparation for defining a Bayesian Network.
# Now with SMILE, the original model can be used. That is a lot easier during research.

categories =  ['Washing Machine', 'Dishwasher', 'Fridge', 'Vacuum Cleaner', 'Personal Care', 'Unknown']
categoryScales = np.array([13.9, 13.2, 16.5, 10.3, 10.8])
categoryShapes = np.array([2.2, 1.6, 2.2, 1.5, 1.3])

brands = ['A', 'B', 'Budget', 'Unknown']
brandCPT = np.array([0.2, 0.5, 0.3])

brandScaleFactors = np.array([1.3, 1.0, 0.7])
brandShapeFactors = np.array([1.3, 1.0, 0.7])

visualConditions = [ 'Packaged', 'Good', 'Fair', 'Poor', 'Unknown']
visualConditionCPT = np.array([ 0.001, 0.009, 0.4, 0.59])

usagesIntensities = [ 'HardlyUsed', 'Light', 'Moderate', 'Heavy', 'Unknown']
usagesIntensityCPT = np.array([[1, 0, 0, 0], [0.1, 0.5, 0.3, 0.2], [0.05, 0.2, 0.55, 0.2], [0.001, 0.009, 0.59, 0.4]])

marketabilities = [ 'Good', 'Bad']
# [visualCondition][usageIntensity][marketability]
marketabilityCPT = np.array([[[0.99, 0.01], [0, 1], [0, 1], [0, 1]], # the last three entries are don't care
                             [[0.9, 0.1], [0.8, 0.2], [0.7, 0.3], [0.1, 0.9]],
                             [[0.8, 0.2], [0.7, 0.3], [0.6, 0.4], [0.05, 0.95]],
                             [[0.3, 0.7], [0.3, 0.7], [0.25, 0.75], [0.05, 0.95]]
                            ])


# Harvestability
harvestabilities = [ 'Good', 'Bad']
# [visualCondition][usageIntensity][harvestability]
harvestabilityCPT = np.array([[[0.99, 0.01], [0, 1], [0, 1], [0, 1]], # the last three entries are don't care
                             [[0.99, 0.01], [0.9, 0.1], [0.5, 0.5], [0.1, 0.9]],
                             [[0.95, 0.05], [0.9, 0.1], [0.5, 0.5], [0.1, 0.9]],
                             [[0.9, 0.1], [0.8, 0.2], [0.4, 0.6], [0.05, 0.95]]
                            ])

age = 8
warrantyPeriod = 1
effectiveScale = 1
effectiveShape = 1
