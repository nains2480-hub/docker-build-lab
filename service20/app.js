const express = require("express");

const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Service 20");
});

app.listen(3000, () => {
  console.log("Service 20 is running");
});
