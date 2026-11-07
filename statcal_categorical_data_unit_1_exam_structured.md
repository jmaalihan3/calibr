```json
{
  "unit": 1,
  "unit_name": "Analyzing Categorical Data",
  "questions": [
    {
      "id": 1,
      "topic": "Analyzing one categorical variable",
      "question": "A researcher records the primary color of cars in a parking lot. Which type of variable is 'car color', and what is the best way to summarize the distribution?",
      "choices": [
        {
          "id": "A",
          "text": "Quantitative; summarized by the mean and standard deviation.",
          "is_correct": false,
          "explanation": "Confuses qualitative categories with quantitative measures, assuming any data collection automatically results in numerical variables suitable for arithmetic mean.",
          "misconception_id": "Q01-M01"
        },
        {
          "id": "B",
          "text": "Categorical; summarized by frequencies or relative frequencies of each category.",
          "is_correct": true,
          "explanation": "Car color is a categorical (qualitative) variable because it places individuals into categories without numerical ordering. Categorical variables are summarized using counts (frequencies) or proportions/percentages (relative frequencies)."
        },
        {
          "id": "C",
          "text": "Quantitative; summarized by a histogram or stem-and-leaf plot.",
          "is_correct": false,
          "explanation": "Mistakes categorical labels for continuous numerical values that can be plotted on a continuous number line (histogram/stemplot).",
          "misconception_id": "Q01-M02"
        },
        {
          "id": "D",
          "text": "Categorical; summarized by the median and interquartile range.",
          "is_correct": false,
          "explanation": "Correctly identifies the variable type as categorical, but incorrectly applies quantitative summary statistics (median and IQR), assuming ordinal ranking exists where none does.",
          "misconception_id": "Q01-M03"
        }
      ],
      "review": {
        "title": "Identifying and summarizing categorical variables",
        "learning_objective": "Classify a variable as categorical and select appropriate frequency-based summaries",
        "related_concepts": [
          "Categorical variables",
          "Qualitative data",
          "Frequency",
          "Relative frequency"
        ]
      }
    },
    {
      "id": 2,
      "topic": "Analyzing one categorical variable",
      "question": "Why is a bar chart generally preferred over a pie chart for displaying categorical data in statistical communication?",
      "choices": [
        {
          "id": "A",
          "text": "Bar charts can display quantitative variables, while pie charts cannot.",
          "is_correct": false,
          "explanation": "Incorrectly assumes bar charts are meant for quantitative data, confusing bar charts with histograms.",
          "misconception_id": "Q02-M01"
        },
        {
          "id": "B",
          "text": "Pie charts require the categories to have a natural numerical ordering.",
          "is_correct": false,
          "explanation": "Falsely attributes numerical ordering requirements to pie charts, which actually represent unordered categorical divisions of a whole.",
          "misconception_id": "Q02-M02"
        },
        {
          "id": "C",
          "text": "Human visual perception is better at comparing lengths of bars than angles or surface areas of slices.",
          "is_correct": true,
          "explanation": "Visual perception studies show that humans are much more accurate at comparing linear heights/lengths than comparing angles or relative slice areas in pie charts."
        },
        {
          "id": "D",
          "text": "Pie charts can only be used when relative frequencies do not sum to 100%.",
          "is_correct": false,
          "explanation": "Reverses the fundamental rule of pie charts: pie charts strictly require categories to sum to 100% (the whole), whereas non-summing relative frequencies require bar charts.",
          "misconception_id": "Q02-M03"
        }
      ],
      "review": {
        "title": "Comparing bar charts and pie charts",
        "learning_objective": "Explain why bar lengths often support more accurate category comparisons than pie-slice angles",
        "related_concepts": [
          "Bar charts",
          "Pie charts",
          "Graphical comparison",
          "Visual perception"
        ]
      }
    },
    {
      "id": 3,
      "topic": "Analyzing one categorical variable",
      "question": "A survey asked respondents for their preferred brand of smartphone. A bar graph was created, but the vertical axis started at 40% instead of 0%. What effect does this visual representation have?",
      "choices": [
        {
          "id": "A",
          "text": "It correctly highlights the small relative differences without distorting the data.",
          "is_correct": false,
          "explanation": "Believes that zooming in on differences is visually neutral, ignoring how linear visual height perception distorts proportion when the baseline is removed.",
          "misconception_id": "Q03-M01"
        },
        {
          "id": "B",
          "text": "It visually exaggerates differences between categories, making small differences look deceptively large.",
          "is_correct": true,
          "explanation": "Truncating the vertical axis (not starting at zero) distorts the proportional visual height of bars, creating a misleading perception that small differences between categories are vast."
        },
        {
          "id": "C",
          "text": "It converts the categorical variable into a quantitative variable.",
          "is_correct": false,
          "explanation": "Confuses graphical display manipulation with a change in the underlying data variable type.",
          "misconception_id": "Q03-M02"
        },
        {
          "id": "D",
          "text": "It alters the actual calculated relative frequencies of the responses.",
          "is_correct": false,
          "explanation": "Conflates the visual scaling of the graph display with the mathematical calculations of the raw underlying data.",
          "misconception_id": "Q03-M03"
        }
      ],
      "review": {
        "title": "Recognizing misleading bar-chart scales",
        "learning_objective": "Explain how a truncated vertical axis can exaggerate differences in categorical frequencies",
        "related_concepts": [
          "Bar charts",
          "Axis scales",
          "Zero baseline",
          "Misleading graphs"
        ]
      }
    },
    {
      "id": 4,
      "topic": "Analyzing one categorical variable",
      "question": "A student wants to plot data on respondents' favorite sport, where respondents were allowed to choose up to two sports. Which display is appropriate?",
      "choices": [
        {
          "id": "A",
          "text": "A pie chart, because it shows parts of a whole.",
          "is_correct": false,
          "explanation": "Fails to recognize that permitting multiple choices breaks the 'mutually exclusive whole' requirement of pie charts.",
          "misconception_id": "Q04-M01"
        },
        {
          "id": "B",
          "text": "A bar chart, because total percentage can exceed 100% when categories overlap.",
          "is_correct": true,
          "explanation": "When respondents can select multiple categories, those categories are not mutually exclusive. Consequently, the sum of category percentages can exceed 100% if some respondents select more than one option. A bar chart is appropriate because it can display each category's frequency or percentage without requiring the categories to partition a single whole."
        },
        {
          "id": "C",
          "text": "A histogram, because preferred sport is a continuous categorical variable.",
          "is_correct": false,
          "explanation": "Contradicts basic variable taxonomy by treating non-numerical categories as a continuous numerical variable.",
          "misconception_id": "Q04-M02"
        },
        {
          "id": "D",
          "text": "A pie chart, by scaling all percentages down so they total 100%.",
          "is_correct": false,
          "explanation": "Thinks mathematical scaling/normalization can fix a structural violation of mutual exclusivity, which distorts true category proportions relative to total sample size.",
          "misconception_id": "Q04-M03"
        }
      ],
      "review": {
        "title": "Displaying multiple-response categories",
        "learning_objective": "Choose an appropriate categorical display when respondents may select multiple categories",
        "related_concepts": [
          "Multiple-response data",
          "Bar charts",
          "Category frequencies",
          "Non-mutually exclusive categories"
        ]
      }
    },
    {
      "id": 5,
      "topic": "Analyzing one categorical variable",
      "question": "In a bar chart displaying frequency of eye color, what does the height of each bar represent?",
      "choices": [
        {
          "id": "A",
          "text": "The proportion of observations falling into each eye color category.",
          "is_correct": false,
          "explanation": "Confuses raw frequency (count) with relative frequency (proportion/percentage).",
          "misconception_id": "Q05-M01"
        },
        {
          "id": "B",
          "text": "The total count of individuals observed in each eye color category.",
          "is_correct": true,
          "explanation": "In a frequency bar chart, the height corresponds to the raw count (frequency) of individuals in each discrete category. A relative frequency bar chart displays proportions or percentages."
        },
        {
          "id": "C",
          "text": "The average value calculated for each eye color.",
          "is_correct": false,
          "explanation": "Erroneously assumes categorical labels possess numerical values that can yield an arithmetic mean.",
          "misconception_id": "Q05-M02"
        },
        {
          "id": "D",
          "text": "The probability of randomly selecting an individual with that eye color.",
          "is_correct": false,
          "explanation": "Confuses raw frequency (the number of observations in a category) with relative frequency or empirical probability (the proportion of observations in that category).",
          "misconception_id": "Q05-M03"
        }
      ],
      "review": {
        "title": "Interpreting bar-chart heights",
        "learning_objective": "Interpret the frequency represented by the height of a bar in a categorical display",
        "related_concepts": [
          "Bar charts",
          "Frequency",
          "Categorical distributions"
        ]
      }
    },
    {
      "id": 6,
      "topic": "Two-way tables",
      "question": "A two-way table summarizes data on student grade level (Freshman, Sophomore, Junior, Senior) and preferred study location (Library, Dorm, Cafe). What do the row totals and column totals represent?",
      "choices": [
        {
          "id": "A",
          "text": "Conditional distributions of preferred study location.",
          "is_correct": false,
          "explanation": "Confuses single-variable totals on the margins with conditional distributions, which restrict attention to a specific subgroup row or column.",
          "misconception_id": "Q06-M01"
        },
        {
          "id": "B",
          "text": "Marginal distributions for each categorical variable individually.",
          "is_correct": true,
          "explanation": "The totals along the margins (row and column totals) give the marginal distributions of each variable separately, ignoring the categories of the other variable."
        },
        {
          "id": "C",
          "text": "Joint distributions showing association between grade level and location.",
          "is_correct": false,
          "explanation": "Mistakes isolated marginal totals for joint intersections where two variables overlap.",
          "misconception_id": "Q06-M02"
        },
        {
          "id": "D",
          "text": "Segmented probabilities of independent events.",
          "is_correct": false,
          "explanation": "Assumes table boundaries imply statistical independence calculations rather than descriptive totals.",
          "misconception_id": "Q06-M03"
        }
      ],
      "review": {
        "title": "Interpreting two-way table totals",
        "learning_objective": "Distinguish marginal totals from individual cell counts in a two-way table",
        "related_concepts": [
          "Two-way frequency tables",
          "Row totals",
          "Column totals",
          "Marginal frequencies"
        ]
      }
    },
    {
      "id": 7,
      "topic": "Two-way tables",
      "question": "When constructing a two-way table to compare two categorical variables, what is a 'joint frequency'?",
      "choices": [
        {
          "id": "A",
          "text": "The total number of observations in a single row.",
          "is_correct": false,
          "explanation": "Confuses joint frequency with marginal frequency (the total count of a single row or column).",
          "misconception_id": "Q07-M01"
        },
        {
          "id": "B",
          "text": "The total sample size across all categories.",
          "is_correct": false,
          "explanation": "Confuses a joint cell count with the grand total sample size ($N$).",
          "misconception_id": "Q07-M02"
        },
        {
          "id": "C",
          "text": "The number of observations that fall into a specific combination of one row category and one column category.",
          "is_correct": true,
          "explanation": "A joint frequency is the count of observations satisfying two specific categorical criteria simultaneously (located at the intersection/cell of a specific row and column)."
        },
        {
          "id": "D",
          "text": "The ratio of a specific row total to the overall table total.",
          "is_correct": false,
          "explanation": "Confuses a frequency count with a relative marginal calculation (a proportion).",
          "misconception_id": "Q07-M03"
        }
      ],
      "review": {
        "title": "Understanding joint frequencies",
        "learning_objective": "Identify a joint frequency as a count in the intersection of two categorical levels",
        "related_concepts": [
          "Two-way frequency tables",
          "Joint frequency",
          "Contingency tables"
        ]
      }
    },
    {
      "id": 8,
      "topic": "Two-way tables",
      "question": "In a two-way table with 100 total participants comparing Exercise (Yes/No) and Heart Disease (Yes/No), 20 people exercise and have no heart disease, while 10 people exercise and have heart disease. What is the joint relative frequency of exercising and having no heart disease?",
      "choices": [
        {
          "id": "A",
          "text": "0.20",
          "is_correct": true,
          "explanation": "The joint relative frequency is the cell count divided by the total sample size: 20 / 100 = 0.20 or 20%."
        },
        {
          "id": "B",
          "text": "0.30",
          "is_correct": false,
          "explanation": "Calculates the marginal relative frequency of exercising overall ($[20+10]/100 = 0.30$) instead of the specific joint cell.",
          "misconception_id": "Q08-M01"
        },
        {
          "id": "C",
          "text": "0.66",
          "is_correct": false,
          "explanation": "Calculates a conditional relative frequency ($20/30 \\approx 0.67$) restricted only to exercisers rather than the joint relative frequency out of the total sample.",
          "misconception_id": "Q08-M02"
        },
        {
          "id": "D",
          "text": "0.10",
          "is_correct": false,
          "explanation": "Selects the incorrect cell ('exercise AND heart disease', $10/100 = 0.10$) rather than 'exercise AND no heart disease'.",
          "misconception_id": "Q08-M03"
        }
      ],
      "review": {
        "title": "Calculating relative frequencies from counts",
        "learning_objective": "Determine an appropriate relative frequency using counts from a two-way table",
        "related_concepts": [
          "Two-way frequency tables",
          "Joint relative frequency",
          "Relative frequency",
          "Grand total"
        ]
      }
    },
    {
      "id": 9,
      "topic": "Two-way tables",
      "question": "Which of the following best describes the difference between a marginal relative frequency and a joint relative frequency?",
      "choices": [
        {
          "id": "A",
          "text": "Marginal relative frequencies consider two variables at once; joint relative frequencies consider only one.",
          "is_correct": false,
          "explanation": "Completely reverses the definitions of marginal and joint frequencies.",
          "misconception_id": "Q09-M01"
        },
        {
          "id": "B",
          "text": "Marginal relative frequencies divide cell counts by row totals; joint relative frequencies divide cell counts by column totals.",
          "is_correct": false,
          "explanation": "Confuses marginal and joint frequencies with two different ways of computing conditional frequencies.",
          "misconception_id": "Q09-M02"
        },
        {
          "id": "C",
          "text": "Marginal relative frequencies describe the distribution of one variable overall; joint relative frequencies describe the proportion of observations meeting criteria for both variables simultaneously.",
          "is_correct": true,
          "explanation": "Marginal relative frequencies analyze one variable isolated in the margins (e.g., total proportion of seniors), whereas joint relative frequencies measure the overlap of two categories (e.g., proportion of seniors who study in the library)."
        },
        {
          "id": "D",
          "text": "Marginal relative frequencies always sum to 100%, whereas joint relative frequencies do not.",
          "is_correct": false,
          "explanation": "Falsely believes joint frequencies across all cells do not sum to 100% of the table total.",
          "misconception_id": "Q09-M03"
        }
      ],
      "review": {
        "title": "Distinguishing joint and marginal relative frequencies",
        "learning_objective": "Differentiate cell-based joint relative frequencies from row- or column-total marginal relative frequencies",
        "related_concepts": [
          "Joint relative frequency",
          "Marginal relative frequency",
          "Two-way tables"
        ]
      }
    },
    {
      "id": 10,
      "topic": "Two-way tables",
      "question": "A table categorizes employees by Department (Sales, IT, HR) and Shift (Day, Night). If you want to know what percentage of all employees work in IT, which calculation should you use?",
      "choices": [
        {
          "id": "A",
          "text": "The total count of IT employees divided by the total count of Day shift employees.",
          "is_correct": false,
          "explanation": "Mistakes a ratio of two unrelated marginal totals for an overall relative frequency.",
          "misconception_id": "Q10-M01"
        },
        {
          "id": "B",
          "text": "The cell count of IT employees on the Day shift divided by the total employee count.",
          "is_correct": false,
          "explanation": "Calculates a joint relative frequency for a specific shift (Day shift IT) instead of the total IT proportion across shifts.",
          "misconception_id": "Q10-M02"
        },
        {
          "id": "C",
          "text": "The marginal total count of IT employees divided by the grand total count of employees.",
          "is_correct": true,
          "explanation": "To find the percentage of all employees in a single category regardless of shift, use the marginal relative frequency: Total IT employees divided by the total number of employees."
        },
        {
          "id": "D",
          "text": "The cell count of IT employees on the Night shift divided by the marginal total of IT employees.",
          "is_correct": false,
          "explanation": "Calculates a conditional relative frequency (IT workers on Night shift given IT status) instead of an overall marginal relative frequency.",
          "misconception_id": "Q10-M03"
        }
      ],
      "review": {
        "title": "Finding a marginal percentage",
        "learning_objective": "Calculate the percentage in one category of a variable using the overall sample total",
        "related_concepts": [
          "Marginal relative frequency",
          "Column totals",
          "Grand total",
          "Percentages"
        ]
      }
    },
    {
      "id": 11,
      "topic": "Distributions in two-way tables",
      "question": "To determine whether there is an association between Voting Preference (Candidate A, Candidate B) and Age Group (Young, Adult, Senior), which distribution should be calculated and compared across age groups?",
      "choices": [
        {
          "id": "A",
          "text": "The marginal distribution of Age Group.",
          "is_correct": false,
          "explanation": "Fails to see that marginal distributions isolate a single variable and completely obscure any relationship between variables.",
          "misconception_id": "Q11-M01"
        },
        {
          "id": "B",
          "text": "The joint relative frequencies for all cells.",
          "is_correct": false,
          "explanation": "Uses joint relative frequencies instead of comparing conditional distributions. Joint relative frequencies use the grand total as their denominator, whereas each conditional distribution uses the size of the relevant age group as its denominator.",
          "misconception_id": "Q11-M02"
        },
        {
          "id": "C",
          "text": "The conditional distributions of Voting Preference for each Age Group.",
          "is_correct": true,
          "explanation": "To investigate an association, compare the conditional distributions of one variable across the categories of the other variable. If the conditional distributions differ, this is evidence of an association in the observed data. Whether that association is statistically significant is a separate inferential question requiring additional analysis."
        },
        {
          "id": "D",
          "text": "The overall grand total frequency.",
          "is_correct": false,
          "explanation": "Confuses sample size aggregation with comparative distribution analysis.",
          "misconception_id": "Q11-M03"
        }
      ],
      "review": {
        "title": "Comparing conditional distributions",
        "learning_objective": "Use conditional distributions to assess association between two categorical variables",
        "related_concepts": [
          "Conditional distributions",
          "Association",
          "Two-way relative frequency tables",
          "Comparing groups"
        ]
      }
    },
    {
      "id": 12,
      "topic": "Distributions in two-way tables",
      "question": "What does it mean for two categorical variables to be statistically independent in a two-way table?",
      "choices": [
        {
          "id": "A",
          "text": "The row totals equal the column totals.",
          "is_correct": false,
          "explanation": "Confuses statistical independence between variables with symmetry in sample category sizes.",
          "misconception_id": "Q12-M01"
        },
        {
          "id": "B",
          "text": "The conditional distribution of one variable is the same across all categories of the other variable.",
          "is_correct": true,
          "explanation": "Two categorical variables are independent (have no association) if knowing the category of one variable gives no additional information about the likelihood of the other variable, meaning conditional distributions are identical across categories."
        },
        {
          "id": "C",
          "text": "All cell frequencies in the table are identical.",
          "is_correct": false,
          "explanation": "Assumes independence requires uniform counts across all joint cells, ignoring different group sample sizes.",
          "misconception_id": "Q12-M02"
        },
        {
          "id": "D",
          "text": "The joint relative frequencies sum to zero.",
          "is_correct": false,
          "explanation": "Mistakes statistical independence for mutually exclusive (disjoint) events that cannot occur together.",
          "misconception_id": "Q12-M03"
        }
      ],
      "review": {
        "title": "Understanding independence of categorical variables",
        "learning_objective": "Describe statistical independence in terms of equal conditional distributions",
        "related_concepts": [
          "Statistical independence",
          "Conditional distributions",
          "Association"
        ]
      }
    },
    {
      "id": 13,
      "topic": "Distributions in two-way tables",
      "question": "A stacked (segmented) bar chart is created to display the relationship between Gender and Preferred Pet (Dog, Cat, Fish). What feature on the chart indicates an association between Gender and Preferred Pet?",
      "choices": [
        {
          "id": "A",
          "text": "The total height of each stacked bar is equal to 100%.",
          "is_correct": false,
          "explanation": "Focuses on a standard formatting feature (100% normalization) rather than visual differences between segments.",
          "misconception_id": "Q13-M01"
        },
        {
          "id": "B",
          "text": "The relative segment proportions within the bars differ across genders.",
          "is_correct": true,
          "explanation": "In a segmented bar chart scaled to 100%, if the relative segment sizes (proportions) differ from one group to another, it shows that the conditional distribution changes based on the group, indicating an association."
        },
        {
          "id": "C",
          "text": "The total number of respondents for each gender is different.",
          "is_correct": false,
          "explanation": "Confuses uneven sample sizes between groups with a statistical relationship between the two variables.",
          "misconception_id": "Q13-M02"
        },
        {
          "id": "D",
          "text": "The bars are arranged in alphabetical order by pet type.",
          "is_correct": false,
          "explanation": "Mistakes non-statistical axis layout conventions for evidence of association.",
          "misconception_id": "Q13-M03"
        }
      ],
      "review": {
        "title": "Reading segmented bar charts",
        "learning_objective": "Recognize association through differences in the composition of segmented bars",
        "related_concepts": [
          "Segmented bar charts",
          "Conditional relative frequencies",
          "Association",
          "Categorical distributions"
        ]
      }
    },
    {
      "id": 14,
      "topic": "Distributions in two-way tables",
      "question": "In a study on Medication (Drug A vs. Placebo) and Recovery (Recovered vs. Not Recovered), 70% of Drug A patients recovered and 30% of Placebo patients recovered. What can be concluded conceptually?",
      "choices": [
        {
          "id": "A",
          "text": "There is no association between Medication type and Recovery outcome.",
          "is_correct": false,
          "explanation": "Assumes there is no association because both groups include recovered and non-recovered patients, overlooking the difference between the conditional recovery rates (70% versus 30%).",
          "misconception_id": "Q14-M01"
        },
        {
          "id": "B",
          "text": "There is an association between Medication type and Recovery outcome because the conditional recovery rates are different.",
          "is_correct": true,
          "explanation": "Since the conditional rate of recovery given Drug A (70%) differs from the conditional rate given Placebo (30%), an association exists between the two variables."
        },
        {
          "id": "C",
          "text": "Drug A caused recovery in exactly 70% of all people in the general population.",
          "is_correct": false,
          "explanation": "Over-generalizes a sample percentage to a definitive causal claim for an entire population without scope-of-inference context.",
          "misconception_id": "Q14-M02"
        },
        {
          "id": "D",
          "text": "The marginal distribution of recovery is equal to the conditional distribution of recovery.",
          "is_correct": false,
          "explanation": "Confuses the overall marginal recovery distribution with the group-specific conditional recovery distributions. The overall recovery rate depends on the relative sizes of the Drug A and placebo groups and cannot be determined from the two conditional rates alone.",
          "misconception_id": "Q14-M03"
        }
      ],
      "review": {
        "title": "Comparing recovery rates across groups",
        "learning_objective": "Interpret differences between conditional recovery rates while distinguishing association from causal inference",
        "related_concepts": [
          "Conditional relative frequency",
          "Association",
          "Treatment groups",
          "Causal inference"
        ]
      }
    },
    {
      "id": 15,
      "topic": "Distributions in two-way tables",
      "question": "When examining conditional relative frequencies in a two-way table, what must always be true about the sum of the conditional proportions within a given condition?",
      "choices": [
        {
          "id": "A",
          "text": "They sum to the total sample size N.",
          "is_correct": false,
          "explanation": "Confuses relative proportions (which sum to 1.0 within a condition) with absolute frequency counts.",
          "misconception_id": "Q15-M01"
        },
        {
          "id": "B",
          "text": "They sum to 1.0 (or 100%) for each category of the condition.",
          "is_correct": true,
          "explanation": "A conditional distribution restricts the sample space to a specific row or column. Therefore, the relative proportions within that row or column must sum to 1 (or 100%)."
        },
        {
          "id": "C",
          "text": "They sum to the marginal frequency of the outcome variable.",
          "is_correct": false,
          "explanation": "Confuses the sum of proportions inside a condition with a single marginal count of an outcome variable.",
          "misconception_id": "Q15-M02"
        },
        {
          "id": "D",
          "text": "They sum to 0.50 across all rows and columns.",
          "is_correct": false,
          "explanation": "Arbitrarily assigns a fixed value of 0.50, misapplying concepts of coin flips or binary splits.",
          "misconception_id": "Q15-M03"
        }
      ],
      "review": {
        "title": "Summing conditional proportions",
        "learning_objective": "Recognize that proportions across exhaustive, mutually exclusive categories within one conditioning group sum to one",
        "related_concepts": [
          "Conditional distributions",
          "Conditional relative frequency",
          "Proportions",
          "Mutually exclusive categories"
        ]
      }
    },
    {
      "id": 16,
      "topic": "Distributions in two-way tables",
      "question": "Simpson's Paradox occurs when an observed association between two categorical variables:",
      "choices": [
        {
          "id": "A",
          "text": "Reverses or disappears when data are aggregated across a third lurking variable.",
          "is_correct": true,
          "explanation": "Simpson's Paradox describes a phenomenon where a trend or association present within several sub-groups reverses or disappears when those groups are combined due to an unaccounted-for lurking variable."
        },
        {
          "id": "B",
          "text": "Is proven to be a direct cause-and-effect relationship.",
          "is_correct": false,
          "explanation": "Incorrectly believes Simpson's Paradox strengthens causal proof, whereas it actually reveals hidden confounding.",
          "misconception_id": "Q16-M01"
        },
        {
          "id": "C",
          "text": "Yields marginal distributions that do not sum to 100%.",
          "is_correct": false,
          "explanation": "Mistakes a statistical paradox involving confounding for a mathematical summation error in table margins.",
          "misconception_id": "Q16-M02"
        },
        {
          "id": "D",
          "text": "Occurs because sample sizes in all conditional groups are equal.",
          "is_correct": false,
          "explanation": "Assumes equal subgroup sample sizes trigger the paradox, when in fact *unequal* subgroup weighting across confounding levels drives Simpson's Paradox.",
          "misconception_id": "Q16-M03"
        }
      ],
      "review": {
        "title": "Understanding Simpson’s paradox",
        "learning_objective": "Explain how aggregation across groups can reverse or obscure a conditional association",
        "related_concepts": [
          "Simpson’s paradox",
          "Confounding variables",
          "Aggregated data",
          "Conditional association"
        ]
      }
    },
    {
      "id": 17,
      "topic": "Analyzing one categorical variable",
      "question": "A researcher collects data on college majors (Business, Engineering, Arts, Science). Which graph is appropriate for displaying this distribution, and which is NOT?",
      "choices": [
        {
          "id": "A",
          "text": "Bar chart is appropriate; Stem-and-leaf plot is NOT appropriate.",
          "is_correct": true,
          "explanation": "College major is a categorical variable. Bar charts display categorical data. Stem-and-leaf plots, histograms, and box plots require quantitative numerical data."
        },
        {
          "id": "B",
          "text": "Histogram is appropriate; Pie chart is NOT appropriate.",
          "is_correct": false,
          "explanation": "Confuses histograms (for continuous quantitative data) with bar charts (for categorical data).",
          "misconception_id": "Q17-M01"
        },
        {
          "id": "C",
          "text": "Box plot is appropriate; Bar chart is NOT appropriate.",
          "is_correct": false,
          "explanation": "Mistakes box plots (quantitative 5-number summaries) as tools for categorical distributions.",
          "misconception_id": "Q17-M02"
        },
        {
          "id": "D",
          "text": "Dot plot is appropriate; Segmented bar chart is NOT appropriate.",
          "is_correct": false,
          "explanation": "Assumes dot plots (quantitative values along a continuous number line) are suitable for discrete named categories.",
          "misconception_id": "Q17-M03"
        }
      ],
      "review": {
        "title": "Selecting graphs for categorical data",
        "learning_objective": "Identify appropriate and inappropriate graphical displays for nominal categorical data",
        "related_concepts": [
          "Categorical variables",
          "Bar charts",
          "Pie charts",
          "Histograms"
        ]
      }
    },
    {
      "id": 18,
      "topic": "Two-way tables",
      "question": "A two-way table records Transportation Method (Car, Bus, Bike) and Punctuality (On-time, Late) for 200 workers. If 40 out of 50 bike commuters arrive on time, what is the conditional relative frequency of being on time, GIVEN that a worker commutes by bike?",
      "choices": [
        {
          "id": "A",
          "text": "0.20",
          "is_correct": false,
          "explanation": "Calculates the joint relative frequency out of the entire sample ($40/200 = 0.20$) instead of conditioning strictly on bike commuters.",
          "misconception_id": "Q18-M01"
        },
        {
          "id": "B",
          "text": "0.25",
          "is_correct": false,
          "explanation": "Calculates the complement ratio of late bike commuters out of on-time bike commuters ($10/40 = 0.25$) or misidentifies the condition.",
          "misconception_id": "Q18-M02"
        },
        {
          "id": "C",
          "text": "0.80",
          "is_correct": true,
          "explanation": "The condition is commuting by bike (N = 50). The count meeting the criterion within this condition is 40. Conditional relative frequency = 40 / 50 = 0.80 (80%)."
        },
        {
          "id": "D",
          "text": "0.10",
          "is_correct": false,
          "explanation": "Calculates the proportion of late bike commuters out of the entire sample ($10/200 = 0.10$).",
          "misconception_id": "Q18-M03"
        }
      ],
      "review": {
        "title": "Calculating a conditional relative frequency",
        "learning_objective": "Use the correct subgroup denominator to calculate a conditional percentage",
        "related_concepts": [
          "Conditional relative frequency",
          "Two-way frequency tables",
          "Subgroup denominators"
        ]
      }
    },
    {
      "id": 19,
      "topic": "Distributions in two-way tables",
      "question": "If two categorical variables show NO association in a sample two-way table, what should a side-by-side bar chart of their conditional distributions look like?",
      "choices": [
        {
          "id": "A",
          "text": "The bars within each group will vary dramatically in height.",
          "is_correct": false,
          "explanation": "Mistakes a strong association (varying conditional profiles across groups) for independence/no association.",
          "misconception_id": "Q19-M01"
        },
        {
          "id": "B",
          "text": "The set of bar heights for each group will look identical or nearly identical across all categories.",
          "is_correct": true,
          "explanation": "When there is no association, the conditional distributions are identical across categories, so side-by-side bar charts will exhibit identical profiles/bar patterns across groups."
        },
        {
          "id": "C",
          "text": "All bars for all categories will be equal to zero.",
          "is_correct": false,
          "explanation": "Confuses the absence of an association (equal relative distributions) with the complete absence of observations.",
          "misconception_id": "Q19-M02"
        },
        {
          "id": "D",
          "text": "The bars for the explanatory variable will be twice as tall as the response variable.",
          "is_correct": false,
          "explanation": "Applies an arbitrary numerical scalar ratio to graph heights instead of looking for identical proportional distributions.",
          "misconception_id": "Q19-M03"
        }
      ],
      "review": {
        "title": "Visualizing a lack of association",
        "learning_objective": "Recognize that similar conditional distributions indicate little or no observed association",
        "related_concepts": [
          "Side-by-side bar charts",
          "Conditional distributions",
          "Statistical independence",
          "Association"
        ]
      }
    },
    {
      "id": 20,
      "topic": "Analyzing one categorical variable",
      "question": "Which of the following statistics can be computed for a purely categorical variable like favorite color?",
      "choices": [
        {
          "id": "A",
          "text": "Mean",
          "is_correct": false,
          "explanation": "Assumes category counts can be added and divided to find an arithmetic average category name.",
          "misconception_id": "Q20-M01"
        },
        {
          "id": "B",
          "text": "Median",
          "is_correct": false,
          "explanation": "Assumes nominal categories have an inherent ordinal rank that allows finding a middle value.",
          "misconception_id": "Q20-M02"
        },
        {
          "id": "C",
          "text": "Mode",
          "is_correct": true,
          "explanation": "Because nominal categorical data have no numerical value or meaningful ordering, measures of center like mean and median, and measures of spread like standard deviation cannot be computed. Only the mode (most frequent category) is applicable."
        },
        {
          "id": "D",
          "text": "Standard Deviation",
          "is_correct": false,
          "explanation": "Believes measures of numerical variability can be computed on non-numerical qualitative labels.",
          "misconception_id": "Q20-M03"
        }
      ],
      "review": {
        "title": "Choosing summaries for nominal data",
        "learning_objective": "Identify appropriate summary statistics for a purely nominal categorical variable",
        "related_concepts": [
          "Nominal variables",
          "Mode",
          "Frequency",
          "Relative frequency"
        ]
      }
    }
  ]
}
```
