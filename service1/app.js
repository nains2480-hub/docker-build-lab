const express = require("express");

const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Service 1");
});

app.listen(3000, () => {
  console.log("Service 1 is running on port 3000");
});
