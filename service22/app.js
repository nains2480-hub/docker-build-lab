const express = require("express");

const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Service 22");
});

app.listen(3000, () => {
  console.log("Service 22 is running");
});
