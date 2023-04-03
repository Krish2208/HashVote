import * as React from "react";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import Divider from "@mui/material/Divider";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Collapse from "@mui/material/Collapse";
import ContactsIcon from "@mui/icons-material/Contacts";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";
import GroupsIcon from "@mui/icons-material/Groups";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ViewListIcon from "@mui/icons-material/ViewList";
import Navbar from "./navbar";
import Main from "./main";

const drawerWidth = 240;

export default function ClippedDrawer() {
  const [open, setOpen] = React.useState(true);
  const [mainScreem, setMainScreen] = React.useState(0);
  const handleClick = () => {
    setOpen(!open);
  };
  return (
    <Box sx={{ display: "flex" }}>
      <ThemeProvider
        theme={createTheme({
          components: {
            MuiListItemButton: {
              defaultProps: {
                disableTouchRipple: true,
              },
            },
          },
          palette: {
            mode: "dark",
            primary: { main: "rgb(102, 157, 246)" },
            background: { paper: "rgb(5, 30, 52)" },
          },
        })}
      >
        <Navbar />
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: {
              width: drawerWidth,
              boxSizing: "border-box",
            },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: "auto" }}>
            <ListItemButton onClick={() => setMainScreen(0)}>
              <ListItemIcon>
                <DashboardIcon />
              </ListItemIcon>
              <ListItemText
                primary="Dashboard"
                primaryTypographyProps={{ fontSize: "18px", fontWeight: 700 }}
              />
            </ListItemButton>
            <Divider />
            <ListItemButton onClick={handleClick}>
              <ListItemText
                primary="Manage"
                primaryTypographyProps={{ fontSize: "18px", fontWeight: 700 }}
                secondary={!open ? "Voters, Positions and Candidates" : null}
              />
              {open ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
            <Collapse in={open} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                <ListItemButton sx={{ pl: 4 }} onClick={() => setMainScreen(1)}>
                  <ListItemIcon>
                    <GroupsIcon />
                  </ListItemIcon>
                  <ListItemText primary="Voters" />
                </ListItemButton>
                <ListItemButton sx={{ pl: 4 }} onClick={() => setMainScreen(2)}>
                  <ListItemIcon>
                    <ViewListIcon />
                  </ListItemIcon>
                  <ListItemText primary="Positions" />
                </ListItemButton>
                <ListItemButton sx={{ pl: 4 }} onClick={() => setMainScreen(3)}>
                  <ListItemIcon>
                    <ContactsIcon />
                  </ListItemIcon>
                  <ListItemText primary="Candidates" />
                </ListItemButton>
              </List>
            </Collapse>
            <Divider />
          </Box>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Main screen={mainScreem}/>
        </Box>
      </ThemeProvider>
    </Box>
  );
}
