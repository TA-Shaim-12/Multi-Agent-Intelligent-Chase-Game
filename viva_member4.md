# Member 4 Viva Preparation

## Q1: What was your role in the project?
My role was Member 4 — Simulated Annealing + UI System. I worked on Simulated Annealing explanation, algorithm comments, UI tooltips, mini scoreboard, MVP officer display, save/load map support, and documentation.

## Q2: Which branch did you work on?
I worked on the branch named sa_0112320269.

## Q3: What is Simulated Annealing?
Simulated Annealing is a probabilistic search and optimization algorithm. It can sometimes accept worse moves at the beginning to explore more paths and avoid local traps.

## Q4: What does temperature mean in Simulated Annealing?
Temperature controls the randomness of the algorithm. High temperature means more exploration. Low temperature means the algorithm becomes more focused on better moves.

## Q5: Why does temperature decrease?
Temperature decreases using a cooling schedule. This allows the algorithm to explore more at first and become stable later.

## Q6: Why is Simulated Annealing useful in a chase game?
In a chase game, the agent may get stuck if it always chooses only the closest or best-looking move. Simulated Annealing can sometimes choose a different move, which helps avoid local traps.

## Q7: What is the difference between Simulated Annealing and Hill Climbing?
Hill Climbing usually chooses the best nearby move and can easily get stuck in local traps. Simulated Annealing can accept worse moves sometimes, so it has a better chance of escaping local traps.

## Q8: Why is A* fallback used?
Simulated Annealing is random and may fail to find the goal within a fixed number of steps. A* fallback is used because it is more reliable and gives a stable final path.

## Q9: What UI features did you add?
I added algorithm tooltip descriptions, mini scoreboard support, MVP officer display, and save/load support for the custom map editor.

## Q10: Why are algorithm tooltips useful?
Algorithm tooltips help users understand the purpose of each algorithm from the menu.

## Q11: Why is the mini scoreboard useful?
The mini scoreboard helps users see game performance information during the chase.

## Q12: What is the MVP officer display?
The MVP officer display shows the best-performing officer based on game performance, such as captures.

## Q13: Why is save/load map support useful?
It allows users to save a custom map and load it again later. This helps in testing, demonstration, and reusing custom game scenarios.

## Q14: How did you follow GitHub guidelines?
I worked only on my own branch, made meaningful commits, opened a pull request, and avoided fake commits or direct changes to the main branch.

## Q15: What is your current PR status?
My pull request is open and waiting for review. I should not merge it myself.
