import React, { useRef, useState, useEffect } from "react";
import usePlacesAutocomplete from "use-places-autocomplete";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import DeleteIcon from "@mui/icons-material/Delete";
import SearchIcon from "@mui/icons-material/Search";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import "./SearchBox.css";

const SearchBox = ({ onSelect, history, setHistory, userLocation }) => {
  const [isFocused, setIsFocused] = useState(false);
  const [hoverIndex, setHoverIndex] = useState(null);
  const ref = useRef(null);

  const {
    ready,
    value,
    setValue,
    suggestions: { status, data },
    clearSuggestions,
  } = usePlacesAutocomplete({
    requestOptions: userLocation
      ? {
          location: new window.google.maps.LatLng(userLocation.lat, userLocation.lng),
          radius: 10000,
        }
      : {},
    debounce: 300,
  });

  useEffect(() => {
    console.log("Places Autocomplete ready:", ready);
  }, [ready]);

  const handleSelect = async (address) => {
    console.log("User pressed search", address);
    setValue("", false);
    clearSuggestions();
    onSelect(address);
    setIsFocused(false);
  };

  const handleDelete = (idx) => {
    const updated = [...history];
    updated.splice(idx, 1);
    setHistory(updated);
    localStorage.setItem("searchHistory", JSON.stringify(updated));
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setIsFocused(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="search-box-container" ref={ref}>
      <div className="search-input-wrapper">
        <SearchIcon className="search-icon" />
        <input
          className="search-input"
          type="text"
          placeholder="Search for an address"
          value={value}
          onFocus={() => {
            console.log("Input focused");
            setIsFocused(true);
          }}
          onChange={(e) => {
            console.log("Input changed:", e.target.value);
            setValue(e.target.value);
          }}
          disabled={!ready}
        />
      </div>

      {isFocused && (
        <div className="dropdown">
          {value === "" && history.length > 0
            ? history.map((item, idx) => (
                <div
                  key={idx}
                  className="dropdown-item"
                  onMouseEnter={() => setHoverIndex(idx)}
                  onMouseLeave={() => setHoverIndex(null)}
                >
                  <AccessTimeIcon className="icon" />
                  <div
                    className="dropdown-text"
                    onClick={() => handleSelect(item.label)}
                    style={{ cursor: "pointer" }}
                  >
                    <Typography variant="body2">{item.label}</Typography>
                    <Typography variant="caption" sx={{ opacity: 0.6 }}>
                      {item.detail}
                    </Typography>
                  </div>
                  {hoverIndex === idx && (
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(idx);
                      }}
                      style={{ marginLeft: "auto" }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  )}
                </div>
              ))
            : status === "OK"
            ? data.map(({ description }, idx) => (
                <div
                  key={idx}
                  className="dropdown-item"
                  onClick={() => handleSelect(description)}
                >
                  <LocationOnIcon className="icon" />
                  <Typography
                    variant="body2"
                    sx={{
                      fontSize: "19px",
                      fontWeight: 400,
                      fontFamily: "'Poppins', sans-serif"
                    }}
                  >
                    {description}
                  </Typography>
                </div>
              ))
            : null}
        </div>
      )}
    </div>
  );
};

export default SearchBox;