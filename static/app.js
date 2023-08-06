async function getTriviaQuestion() {
  response = await axios.get("/random_questions");
  print(response);
}
