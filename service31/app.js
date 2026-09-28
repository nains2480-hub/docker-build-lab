const express = require("express");

const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Service 31");
});

app.listen(3000, () => {
  console.log("Service 31 is running");
});
