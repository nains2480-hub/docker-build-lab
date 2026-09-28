const express = require("express");

const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Service 7");
});

app.listen(3000, () => {
  console.log("Service 7 is running");
});
// New change
