# Election Prediction Markets

This project is about the 2024 national presidential election, and the prediction markets surrounding it.

---

As of May 11, 2024, prediction markets have a BLUE presidential victory at 45%.

However, each state has its own prediction market as well, for whether it will go BLUE or RED.

With a monte carlo simulation, we can calculate the probability of a national BLUE presidential victory, weighting each state's results by its electoral college value and summing the result.

As of May 11, 2024, prediction markets by state have a BLUE presidential victory at 38%.

This 7 point gap is what I am using this project to explore.

### Current capabilities

- Use `/utilities/datagen.py` to generate randomized test data
- Use `/polymarket/polymarket.py` to pull live prediction market prices
- Use `/utilities/simulate_election.py NUM_GENS` to predict the outcome of an election based on most recent data
  - `NUM_GENS`: number of generations to use for the monte carlo simulation
- Use `/utilities/analyze_results.py` to find the most undervalued markets on the state side (assuming a blue win)

### Roadmap

- [x] Pull prediction data from Polymarket
- [ ] Visualize predictions in a web browser
- [ ] Data analysis, written report
- [ ] Clean up this wacky project structure :D
