import React from "react";
import Dashboard from "./dashboard";
import Voters from "./voters";
export default function Main(props) {
  console.log(props)
  return props.screen === 0 ? (
    <Dashboard />
  ) : props.screen === 1 ? (
    <Voters />
  ) : (
    <Dashboard />
  );
}
