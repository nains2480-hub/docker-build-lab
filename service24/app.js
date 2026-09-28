const express = require("express");

const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Service 24");
});

app.listen(3000, () => {
  console.log("Service 24 is running");
});
