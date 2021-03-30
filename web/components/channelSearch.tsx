import {
  FilledInput,
  FormControl,
  Icon,
  Input,
  InputAdornment,
  InputLabel,
  TextField,
} from "@material-ui/core";
import React, { useRef, useState } from "react";
import { Autocomplete } from "@material-ui/lab";
import { getChannelNames } from "lib/api";
import Cookies from "js-cookie";
import { useRouter } from "next/dist/client/router";

export default function ChannelSearch() {
  const [options, setOptions] = useState(["HHGYM"]);
  const inputRef = useRef<HTMLDivElement>();
  const router = useRouter();

  return (
    <Autocomplete
      freeSolo
      options={options}
      getOptionLabel={(lbl) => lbl}
      onClose={(event, reason) => {
        if (reason == "select-option") {
          setTimeout(() =>
            router.push(
              `/posts/${
                inputRef.current.getElementsByTagName("input")[0].value
              }`
            )
          );
        }
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Suche"
          variant="filled"
          innerRef={inputRef}
          onChange={(event) => {
            getChannelNames(
              Cookies.get("token"),
              event.target.value
            ).then((names) => setOptions(names));
          }}
        />
      )}
    />
  );
}
