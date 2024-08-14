import React, { useState } from "react";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import Container from "@mui/material/Container";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import DirectionsIcon from "@mui/icons-material/Directions";
import RefreshIcon from "@mui/icons-material/Refresh";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Drawer from "@mui/material/Drawer";
import Modal from "@mui/material/Modal";
import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";
import Grid from "@mui/material/Grid";
import Button from "@mui/material/Button";
import Map from "./components/map";
import Graph from "./components/graph";
import { nodes } from "./utils/constants";

const style = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 1500,
  bgcolor: "background.paper",
  border: "2px solid #000",
  boxShadow: 24,
  p: 4,
};

export default function App() {
  const [path, setPath] = useState([]);
  const [optimalPath, setOptimalPath] = useState([]);
  const [display, setDisplay] = useState("map");
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const toggleNodeOnPath = (node, checked) => {
    const newPath = path;

    if (checked) {
      newPath.push({
        id: node.Location,
        lat: node.Latitude,
        lon: node.Longitude,
      });
    } else {
      const index = newPath.findIndex(
        (pathNode) => pathNode.id === node.Location
      );

      if (index !== -1) {
        newPath.splice(index, 1);
      }
    }

    setPath(newPath);
  };

  const findOptimalRoute = async () => {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: path }),
    };
    const response = await fetch(
      "http://localhost:5000/tsp/optimize_route",
      requestOptions
    ).then((res) => res.json());

    console.log(path)
    console.log("response:", nodes.filter((node) => response["brute_force"].includes(node.Location)));

    const target = response["brute_force"].map((id) => {
      return nodes.find((node) => node.Location === id)
    });

    setOptimalPath(target.map((node) =>  {
      return {
        id: node.Location,
        lat: node.Latitude,
        lon: node.Longitude
      }
    }));
  }

  return (
    <Container disableGutters maxWidth={false}>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar color="primary">
          <Toolbar>
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              aria-label="menu"
              sx={{ mr: 2 }}
              onClick={() => setIsDrawerOpen(true)}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Optimal Delivery Route System
            </Typography>
            <ToggleButtonGroup
              color="secondary"
              value={display}
              exclusive
              onChange={(event, newDisplay) => setDisplay(newDisplay)}
            >
              <ToggleButton value="map">Map</ToggleButton>
            </ToggleButtonGroup>
            <Drawer
              color="primary"
              open={isDrawerOpen}
              onClose={() => setIsDrawerOpen(false)}
            >
              <Box
                sx={{ width: 250 }}
                onClick={() => setIsDrawerOpen(false)}
                onKeyDown={() => setIsDrawerOpen(false)}
              >
                <List>
                  <ListItem disablePadding>
                    <ListItemButton
                      onClick={() => {
                        setIsModalOpen(true);
                        setPath([]);
                      }}
                    >
                      <ListItemIcon>
                        <DirectionsIcon />
                      </ListItemIcon>
                      <ListItemText primary="Find Optimal Route" />
                    </ListItemButton>
                  </ListItem>
                  <ListItem disablePadding>
                    <ListItemButton
                      onClick={() => {
                        setPath([]);
                        setOptimalPath([]);
                      }}
                    >
                      <ListItemIcon>
                        <RefreshIcon />
                      </ListItemIcon>
                      <ListItemText primary="Reset" />
                    </ListItemButton>
                  </ListItem>
                </List>
              </Box>
            </Drawer>
          </Toolbar>
        </AppBar>
      </Box>

      {
        {
          map: <Map
              path={optimalPath}
          />,
          graph: <Graph path={[]} />,
        }[display]
      }

      <Modal
          open={isModalOpen}
          onClose={() => setIsModalOpen(false)}>
        <Box sx={style}>
          <Typography variant="h6" component="h2">
            Select Delivery Locations
          </Typography>
          <FormGroup>
            <Grid
              container
              rowSpacing={1}
              columnSpacing={{ xs: 1, sm: 2, md: 3 }}
            >
              {nodes.map((node) => (
                <Grid item key={node.Location} xs={3}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        // checked={path.find(
                        //   (pathNode) => pathNode.id === node.Location
                        // )}
                        onChange={(event) =>
                          toggleNodeOnPath(node, event.target.checked)
                        }
                      />
                    }
                    label={node.Location}
                  />
                </Grid>
              ))}
            </Grid>
          </FormGroup>
          <Button
            variant="contained"
            onClick={() => {
              setIsModalOpen(false);
              findOptimalRoute();
            }}
          >
            Find Optimal Route
          </Button>
        </Box>
      </Modal>
    </Container>
  );
}
