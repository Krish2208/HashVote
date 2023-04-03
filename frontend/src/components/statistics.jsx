import {
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  Box,
} from "@mui/material";
import GroupsIcon from "@mui/icons-material/Groups";
import ViewListIcon from "@mui/icons-material/ViewList";
import ContactsIcon from "@mui/icons-material/Contacts";
import React from "react";

function StatCard(props) {
  return (
    <Card sx={{ display: "flex" }}>
      <CardContent sx={{ flex: "1 0 auto" }}>
        <Typography component="div" variant="h5" sx={{fontWeight: 600}}>
          {props.heading}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" component="div">
          {props.value}
        </Typography>
      </CardContent>
      <Box sx={{ display: "flex", alignItems: "center", pr: 4 }}>
        <Avatar
          sx={{
            height: "60px",
            width: "60px",
            backgroundColor: "#DFEBF8",
            border: "1px solid #fff",
          }}
        >
          {props.icon}
        </Avatar>
      </Box>
    </Card>
  );
}

export default function Statistics() {
  return (
    <Grid container spacing={2}>
      <Grid item md={4}>
        <StatCard heading={"Voters"} value={"2442"} icon={<GroupsIcon sx={{ fontSize: "50px", color: "#051E34" }} />}/>
      </Grid>
      <Grid item md={4}>
        <StatCard heading={"Positions"} value={"13"} icon={<ViewListIcon sx={{ fontSize: "50px", color: "#051E34" }} />}/>
      </Grid>
      <Grid item md={4}>
        <StatCard heading={"Candidates"} value={"27"} icon={<ContactsIcon sx={{ fontSize: "40px", color: "#051E34" }} />}/>
      </Grid>
    </Grid>
  );
}
