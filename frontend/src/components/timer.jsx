import { Card, CardContent, Grid, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import React from "react";

export default function Timer() {
  const calculateTimeLeft = () => {
    let year = new Date().getFullYear();
    const difference = +new Date(`${year}-3-30`) - +new Date();
    let timeLeft = {};

    if (difference > 0) {
      timeLeft = {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60),
      };
    }

    return timeLeft;
  };

  const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());
  const [year] = useState(new Date().getFullYear());

  useEffect(() => {
    setTimeout(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);
  });

  const timerComponents = [];

  Object.keys(timeLeft).forEach((interval) => {
    if (!timeLeft[interval]) {
      return;
    }

    timerComponents.push(
      <span>
        {timeLeft[interval]} {interval}{" "}
      </span>
    );
  });

  timerComponents.push(<span>until the next election</span>);

  return (
    <Grid container spacing={2} sx={{ pt: 2 }}>
      <Grid item md={6}>
        <Card>
          <CardContent>
            <Typography component="div" variant="h4" sx={{ fontWeight: 600 }}>
              {timerComponents.length ? timerComponents : <span>Time's up!</span>}
            </Typography>
            <Typography
              variant="subtitle1"
              color="text.secondary"
              component="div"
            >
              Hello
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item md={6}>
        <Card>
          <CardContent>
            <Typography component="div" variant="h5" sx={{ fontWeight: 600 }}>
              Hello
            </Typography>
            <Typography
              variant="subtitle1"
              color="text.secondary"
              component="div"
            >
              Hello
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
