const express = require("express");

const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Service 6");
});

app.listen(3000, () => {
  console.log("Service 6 is running");
});
