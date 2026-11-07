{
  "unit": 1,
  "unit_name": "Analyzing Categorical Data",
  "questions": [
    {
      "id": 1,
      "topic": "Analyzing one categorical variable",
      "question": "A researcher records the primary color of cars in a parking lot. Which type of variable is 'car color', and what is the best way to summarize the distribution?",
      "options": [
        "Quantitative; summarized by the mean and standard deviation.",
        "Categorical; summarized by frequencies or relative frequencies of each category.",
        "Quantitative; summarized by a histogram or stem-and-leaf plot.",
        "Categorical; summarized by the median and interquartile range."
      ],
      "correct": 1,
      "explanation": "Car color is a categorical (qualitative) variable because it places individuals into categories without numerical ordering. Categorical variables are summarized using counts (frequencies) or proportions/percentages (relative frequencies).",
      "misconceptions": {
        "0": "Confuses qualitative categories with quantitative measures, assuming any data collection automatically results in numerical variables suitable for arithmetic mean.",
        "2": "Mistakes categorical labels for continuous numerical values that can be plotted on a continuous number line (histogram/stemplot).",
        "3": "Correctly identifies the variable type as categorical, but incorrectly applies quantitative summary statistics (median and IQR), assuming ordinal ranking exists where none does."
      }
    },
    {
      "id": 2,
      "topic": "Analyzing one categorical variable",
      "question": "Why is a bar chart generally preferred over a pie chart for displaying categorical data in statistical communication?",
      "options": [
        "Bar charts can display quantitative variables, while pie charts cannot.",
        "Pie charts require the categories to have a natural numerical ordering.",
        "Human visual perception is better at comparing lengths of bars than angles or surface areas of slices.",
        "Pie charts can only be used when relative frequencies do not sum to 100%."
      ],
      "correct": 2,
      "explanation": "Visual perception studies show that humans are much more accurate at comparing linear heights/lengths than comparing angles or relative slice areas in pie charts.",
      "misconceptions": {
        "0": "Incorrectly assumes bar charts are meant for quantitative data, confusing bar charts with histograms.",
        "1": "Falsely attributes numerical ordering requirements to pie charts, which actually represent unordered categorical divisions of a whole.",
        "3": "Reverses the fundamental rule of pie charts: pie charts strictly require categories to sum to 100% (the whole), whereas non-summing relative frequencies require bar charts."
      }
    },
    {
      "id": 3,
      "topic": "Analyzing one categorical variable",
      "question": "A survey asked respondents for their preferred brand of smartphone. A bar graph was created, but the vertical axis started at 40% instead of 0%. What effect does this visual representation have?",
      "options": [
        "It correctly highlights the small relative differences without distorting the data.",
        "It visually exaggerates differences between categories, making small differences look deceptively large.",
        "It converts the categorical variable into a quantitative variable.",
        "It alters the actual calculated relative frequencies of the responses."
      ],
      "correct": 1,
      "explanation": "Truncating the vertical axis (not starting at zero) distorts the proportional visual height of bars, creating a misleading perception that small differences between categories are vast.",
      "misconceptions": {
        "0": "Believes that zooming in on differences is visually neutral, ignoring how linear visual height perception distorts proportion when the baseline is removed.",
        "2": "Confuses graphical display manipulation with a change in the underlying data variable type.",
        "3": "Conflates the visual scaling of the graph display with the mathematical calculations of the raw underlying data."
      }
    },
    {
      "id": 4,
      "topic": "Analyzing one categorical variable",
      "question": "A student wants to plot data on respondents' favorite sport, where respondents were allowed to choose up to two sports. Which display is appropriate?",
      "options": [
        "A pie chart, because it shows parts of a whole.",
        "A bar chart, because total percentage can exceed 100% when categories overlap.",
        "A histogram, because preferred sport is a continuous categorical variable.",
        "A pie chart, by scaling all percentages down so they total 100%."
      ],
      "correct": 1,
      "explanation": "When respondents can select multiple categories, those categories are not mutually exclusive. Consequently, the sum of category percentages can exceed 100% if some respondents select more than one option. A bar chart is appropriate because it can display each category's frequency or percentage without requiring the categories to partition a single whole.",
      "misconceptions": {
        "0": "Fails to recognize that permitting multiple choices breaks the 'mutually exclusive whole' requirement of pie charts.",
        "2": "Contradicts basic variable taxonomy by treating non-numerical categories as a continuous numerical variable.",
        "3": "Thinks mathematical scaling/normalization can fix a structural violation of mutual exclusivity, which distorts true category proportions relative to total sample size."
      }
    },
    {
      "id": 5,
      "topic": "Analyzing one categorical variable",
      "question": "In a bar chart displaying frequency of eye color, what does the height of each bar represent?",
      "options": [
        "The proportion of observations falling into each eye color category.",
        "The total count of individuals observed in each eye color category.",
        "The average value calculated for each eye color.",
        "The probability of randomly selecting an individual with that eye color."
      ],
      "correct": 1,
      "explanation": "In a frequency bar chart, the height corresponds to the raw count (frequency) of individuals in each discrete category. A relative frequency bar chart displays proportions or percentages.",
      "misconceptions": {
        "0": "Confuses raw frequency (count) with relative frequency (proportion/percentage).",
        "2": "Erroneously assumes categorical labels possess numerical values that can yield an arithmetic mean.",
        "3": "Confuses raw frequency (the number of observations in a category) with relative frequency or empirical probability (the proportion of observations in that category)."
      }
    },
    {
      "id": 6,
      "topic": "Two-way tables",
      "question": "A two-way table summarizes data on student grade level (Freshman, Sophomore, Junior, Senior) and preferred study location (Library, Dorm, Cafe). What do the row totals and column totals represent?",
      "options": [
        "Conditional distributions of preferred study location.",
        "Marginal distributions for each categorical variable individually.",
        "Joint distributions showing association between grade level and location.",
        "Segmented probabilities of independent events."
      ],
      "correct": 1,
      "explanation": "The totals along the margins (row and column totals) give the marginal distributions of each variable separately, ignoring the categories of the other variable.",
      "misconceptions": {
        "0": "Confuses single-variable totals on the margins with conditional distributions, which restrict attention to a specific subgroup row or column.",
        "2": "Mistakes isolated marginal totals for joint intersections where two variables overlap.",
        "3": "Assumes table boundaries imply statistical independence calculations rather than descriptive totals."
      }
    },
    {
      "id": 7,
      "topic": "Two-way tables",
      "question": "When constructing a two-way table to compare two categorical variables, what is a 'joint frequency'?",
      "options": [
        "The total number of observations in a single row.",
        "The total sample size across all categories.",
        "The number of observations that fall into a specific combination of one row category and one column category.",
        "The ratio of a specific row total to the overall table total."
      ],
      "correct": 2,
      "explanation": "A joint frequency is the count of observations satisfying two specific categorical criteria simultaneously (located at the intersection/cell of a specific row and column).",
      "misconceptions": {
        "0": "Confuses joint frequency with marginal frequency (the total count of a single row or column).",
        "1": "Confuses a joint cell count with the grand total sample size ($N$).",
        "3": "Confuses a frequency count with a relative marginal calculation (a proportion)."
      }
    },
    {
      "id": 8,
      "topic": "Two-way tables",
      "question": "In a two-way table with 100 total participants comparing Exercise (Yes/No) and Heart Disease (Yes/No), 20 people exercise and have no heart disease, while 10 people exercise and have heart disease. What is the joint relative frequency of exercising and having no heart disease?",
      "options": [
        "0.20",
        "0.30",
        "0.66",
        "0.10"
      ],
      "correct": 0,
      "explanation": "The joint relative frequency is the cell count divided by the total sample size: 20 / 100 = 0.20 or 20%.",
      "misconceptions": {
        "1": "Calculates the marginal relative frequency of exercising overall ($[20+10]/100 = 0.30$) instead of the specific joint cell.",
        "2": "Calculates a conditional relative frequency ($20/30 \\approx 0.67$) restricted only to exercisers rather than the joint relative frequency out of the total sample.",
        "3": "Selects the incorrect cell ('exercise AND heart disease', $10/100 = 0.10$) rather than 'exercise AND no heart disease'."
      }
    },
    {
      "id": 9,
      "topic": "Two-way tables",
      "question": "Which of the following best describes the difference between a marginal relative frequency and a joint relative frequency?",
      "options": [
        "Marginal relative frequencies consider two variables at once; joint relative frequencies consider only one.",
        "Marginal relative frequencies divide cell counts by row totals; joint relative frequencies divide cell counts by column totals.",
        "Marginal relative frequencies describe the distribution of one variable overall; joint relative frequencies describe the proportion of observations meeting criteria for both variables simultaneously.",
        "Marginal relative frequencies always sum to 100%, whereas joint relative frequencies do not."
      ],
      "correct": 2,
      "explanation": "Marginal relative frequencies analyze one variable isolated in the margins (e.g., total proportion of seniors), whereas joint relative frequencies measure the overlap of two categories (e.g., proportion of seniors who study in the library).",
      "misconceptions": {
        "0": "Completely reverses the definitions of marginal and joint frequencies.",
        "1": "Confuses marginal and joint frequencies with two different ways of computing conditional frequencies.",
        "3": "Falsely believes joint frequencies across all cells do not sum to 100% of the table total."
      }
    },
    {
      "id": 10,
      "topic": "Two-way tables",
      "question": "A table categorizes employees by Department (Sales, IT, HR) and Shift (Day, Night). If you want to know what percentage of all employees work in IT, which calculation should you use?",
      "options": [
        "The total count of IT employees divided by the total count of Day shift employees.",
        "The cell count of IT employees on the Day shift divided by the total employee count.",
        "The marginal total count of IT employees divided by the grand total count of employees.",
        "The cell count of IT employees on the Night shift divided by the marginal total of IT employees."
      ],
      "correct": 2,
      "explanation": "To find the percentage of all employees in a single category regardless of shift, use the marginal relative frequency: Total IT employees divided by the total number of employees.",
      "misconceptions": {
        "0": "Mistakes a ratio of two unrelated marginal totals for an overall relative frequency.",
        "1": "Calculates a joint relative frequency for a specific shift (Day shift IT) instead of the total IT proportion across shifts.",
        "3": "Calculates a conditional relative frequency (IT workers on Night shift given IT status) instead of an overall marginal relative frequency."
      }
    },
    {
      "id": 11,
      "topic": "Distributions in two-way tables",
      "question": "To determine whether there is an association between Voting Preference (Candidate A, Candidate B) and Age Group (Young, Adult, Senior), which distribution should be calculated and compared across age groups?",
      "options": [
        "The marginal distribution of Age Group.",
        "The joint relative frequencies for all cells.",
        "The conditional distributions of Voting Preference for each Age Group.",
        "The overall grand total frequency."
      ],
      "correct": 2,
      "explanation": "To investigate an association, compare the conditional distributions of one variable across the categories of the other variable. If the conditional distributions differ, this is evidence of an association in the observed data. Whether that association is statistically significant is a separate inferential question requiring additional analysis.",
      "misconceptions": {
        "0": "Fails to see that marginal distributions isolate a single variable and completely obscure any relationship between variables.",
        "1": "Uses joint relative frequencies instead of comparing conditional distributions. Joint relative frequencies use the grand total as their denominator, whereas each conditional distribution uses the size of the relevant age group as its denominator.",
        "3": "Confuses sample size aggregation with comparative distribution analysis."
      }
    },
    {
      "id": 12,
      "topic": "Distributions in two-way tables",
      "question": "What does it mean for two categorical variables to be statistically independent in a two-way table?",
      "options": [
        "The row totals equal the column totals.",
        "The conditional distribution of one variable is the same across all categories of the other variable.",
        "All cell frequencies in the table are identical.",
        "The joint relative frequencies sum to zero."
      ],
      "correct": 1,
      "explanation": "Two categorical variables are independent (have no association) if knowing the category of one variable gives no additional information about the likelihood of the other variable, meaning conditional distributions are identical across categories.",
      "misconceptions": {
        "0": "Confuses statistical independence between variables with symmetry in sample category sizes.",
        "2": "Assumes independence requires uniform counts across all joint cells, ignoring different group sample sizes.",
        "3": "Mistakes statistical independence for mutually exclusive (disjoint) events that cannot occur together."
      }
    },
    {
      "id": 13,
      "topic": "Distributions in two-way tables",
      "question": "A stacked (segmented) bar chart is created to display the relationship between Gender and Preferred Pet (Dog, Cat, Fish). What feature on the chart indicates an association between Gender and Preferred Pet?",
      "options": [
        "The total height of each stacked bar is equal to 100%.",
        "The relative segment proportions within the bars differ across genders.",
        "The total number of respondents for each gender is different.",
        "The bars are arranged in alphabetical order by pet type."
      ],
      "correct": 1,
      "explanation": "In a segmented bar chart scaled to 100%, if the relative segment sizes (proportions) differ from one group to another, it shows that the conditional distribution changes based on the group, indicating an association.",
      "misconceptions": {
        "0": "Focuses on a standard formatting feature (100% normalization) rather than visual differences between segments.",
        "2": "Confuses uneven sample sizes between groups with a statistical relationship between the two variables.",
        "3": "Mistakes non-statistical axis layout conventions for evidence of association."
      }
    },
    {
      "id": 14,
      "topic": "Distributions in two-way tables",
      "question": "In a study on Medication (Drug A vs. Placebo) and Recovery (Recovered vs. Not Recovered), 70% of Drug A patients recovered and 30% of Placebo patients recovered. What can be concluded conceptually?",
      "options": [
        "There is no association between Medication type and Recovery outcome.",
        "There is an association between Medication type and Recovery outcome because the conditional recovery rates are different.",
        "Drug A caused recovery in exactly 70% of all people in the general population.",
        "The marginal distribution of recovery is equal to the conditional distribution of recovery."
      ],
      "correct": 1,
      "explanation": "Since the conditional rate of recovery given Drug A (70%) differs from the conditional rate given Placebo (30%), an association exists between the two variables.",
      "misconceptions": {
        "0": "Assumes there is no association because both groups include recovered and non-recovered patients, overlooking the difference between the conditional recovery rates (70% versus 30%).",
        "2": "Over-generalizes a sample percentage to a definitive causal claim for an entire population without scope-of-inference context.",
        "3": "Confuses the overall marginal recovery distribution with the group-specific conditional recovery distributions. The overall recovery rate depends on the relative sizes of the Drug A and placebo groups and cannot be determined from the two conditional rates alone."
      }
    },
    {
      "id": 15,
      "topic": "Distributions in two-way tables",
      "question": "When examining conditional relative frequencies in a two-way table, what must always be true about the sum of the conditional proportions within a given condition?",
      "options": [
        "They sum to the total sample size N.",
        "They sum to 1.0 (or 100%) for each category of the condition.",
        "They sum to the marginal frequency of the outcome variable.",
        "They sum to 0.50 across all rows and columns."
      ],
      "correct": 1,
      "explanation": "A conditional distribution restricts the sample space to a specific row or column. Therefore, the relative proportions within that row or column must sum to 1 (or 100%).",
      "misconceptions": {
        "0": "Confuses relative proportions (which sum to 1.0 within a condition) with absolute frequency counts.",
        "2": "Confuses the sum of proportions inside a condition with a single marginal count of an outcome variable.",
        "3": "Arbitrarily assigns a fixed value of 0.50, misapplying concepts of coin flips or binary splits."
      }
    },
    {
      "id": 16,
      "topic": "Distributions in two-way tables",
      "question": "Simpson's Paradox occurs when an observed association between two categorical variables:",
      "options": [
        "Reverses or disappears when data are aggregated across a third lurking variable.",
        "Is proven to be a direct cause-and-effect relationship.",
        "Yields marginal distributions that do not sum to 100%.",
        "Occurs because sample sizes in all conditional groups are equal."
      ],
      "correct": 0,
      "explanation": "Simpson's Paradox describes a phenomenon where a trend or association present within several sub-groups reverses or disappears when those groups are combined due to an unaccounted-for lurking variable.",
      "misconceptions": {
        "1": "Incorrectly believes Simpson's Paradox strengthens causal proof, whereas it actually reveals hidden confounding.",
        "2": "Mistakes a statistical paradox involving confounding for a mathematical summation error in table margins.",
        "3": "Assumes equal subgroup sample sizes trigger the paradox, when in fact *unequal* subgroup weighting across confounding levels drives Simpson's Paradox."
      }
    },
    {
      "id": 17,
      "topic": "Analyzing one categorical variable",
      "question": "A researcher collects data on college majors (Business, Engineering, Arts, Science). Which graph is appropriate for displaying this distribution, and which is NOT?",
      "options": [
        "Bar chart is appropriate; Stem-and-leaf plot is NOT appropriate.",
        "Histogram is appropriate; Pie chart is NOT appropriate.",
        "Box plot is appropriate; Bar chart is NOT appropriate.",
        "Dot plot is appropriate; Segmented bar chart is NOT appropriate."
      ],
      "correct": 0,
      "explanation": "College major is a categorical variable. Bar charts display categorical data. Stem-and-leaf plots, histograms, and box plots require quantitative numerical data.",
      "misconceptions": {
        "1": "Confuses histograms (for continuous quantitative data) with bar charts (for categorical data).",
        "2": "Mistakes box plots (quantitative 5-number summaries) as tools for categorical distributions.",
        "3": "Assumes dot plots (quantitative values along a continuous number line) are suitable for discrete named categories."
      }
    },
    {
      "id": 18,
      "topic": "Two-way tables",
      "question": "A two-way table records Transportation Method (Car, Bus, Bike) and Punctuality (On-time, Late) for 200 workers. If 40 out of 50 bike commuters arrive on time, what is the conditional relative frequency of being on time, GIVEN that a worker commutes by bike?",
      "options": [
        "0.20",
        "0.25",
        "0.80",
        "0.10"
      ],
      "correct": 2,
      "explanation": "The condition is commuting by bike (N = 50). The count meeting the criterion within this condition is 40. Conditional relative frequency = 40 / 50 = 0.80 (80%).",
      "misconceptions": {
        "0": "Calculates the joint relative frequency out of the entire sample ($40/200 = 0.20$) instead of conditioning strictly on bike commuters.",
        "1": "Calculates the complement ratio of late bike commuters out of on-time bike commuters ($10/40 = 0.25$) or misidentifies the condition.",
        "3": "Calculates the proportion of late bike commuters out of the entire sample ($10/200 = 0.10$)."
      }
    },
    {
      "id": 19,
      "topic": "Distributions in two-way tables",
      "question": "If two categorical variables show NO association in a sample two-way table, what should a side-by-side bar chart of their conditional distributions look like?",
      "options": [
        "The bars within each group will vary dramatically in height.",
        "The set of bar heights for each group will look identical or nearly identical across all categories.",
        "All bars for all categories will be equal to zero.",
        "The bars for the explanatory variable will be twice as tall as the response variable."
      ],
      "correct": 1,
      "explanation": "When there is no association, the conditional distributions are identical across categories, so side-by-side bar charts will exhibit identical profiles/bar patterns across groups.",
      "misconceptions": {
        "0": "Mistakes a strong association (varying conditional profiles across groups) for independence/no association.",
        "2": "Confuses the absence of an association (equal relative distributions) with the complete absence of observations.",
        "3": "Applies an arbitrary numerical scalar ratio to graph heights instead of looking for identical proportional distributions."
      }
    },
    {
      "id": 20,
      "topic": "Analyzing one categorical variable",
      "question": "Which of the following statistics can be computed for a purely categorical variable like favorite color?",
      "options": [
        "Mean",
        "Median",
        "Mode",
        "Standard Deviation"
      ],
      "correct": 2,
      "explanation": "Because nominal categorical data have no numerical value or meaningful ordering, measures of center like mean and median, and measures of spread like standard deviation cannot be computed. Only the mode (most frequent category) is applicable.",
      "misconceptions": {
        "0": "Assumes category counts can be added and divided to find an arithmetic average category name.",
        "1": "Assumes nominal categories have an inherent ordinal rank that allows finding a middle value.",
        "3": "Believes measures of numerical variability can be computed on non-numerical qualitative labels."
      }
    }
  ]
}
