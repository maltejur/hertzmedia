import {
  Button,
  Card,
  CardContent,
  LinearProgress,
  makeStyles,
  TextField,
  Typography,
} from "@material-ui/core";
import { createUser, loginpermanent } from "lib/api";
import { GetServerSideProps } from "next";
import { useRef, useState } from "react";
import Cookies from "js-cookie";
import { useRouter } from "next/dist/client/router";

const useStyles = makeStyles({
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "70vh",
  },
  card: {
    padding: "20px",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
  },
  input: {
    marginTop: "20px",
    width: "250px",
  },
  loginBtn: {
    marginTop: "20px",
    alignSelf: "flex-end",
  },
});

export default function Register() {
  const classes = useStyles();
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [klasse, setKlasse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const router = useRouter();

  return (
    <div className={classes.container}>
      <Card>
        <LinearProgress style={{ opacity: loading ? 1 : 0 }} />
        <CardContent className={classes.card}>
          <form
            className={classes.form}
            onSubmit={(event) => {
              event.preventDefault();
              setError(false);
              setLoading(true);
              createUser(user, password, klasse)
                .then((token) => {
                  Cookies.set("token", token);
                  router.push("/");
                })
                .catch(() => {
                  setError(true);
                  setLoading(false);
                });
            }}
          >
            <Typography variant="h4">Registrieren</Typography>
            <TextField
              value={user}
              onChange={(event) => setUser(event.target.value)}
              required
              className={classes.input}
              variant="outlined"
              label="User"
              disabled={loading}
              error={error}
              helperText={
                error ? "Username wurde noch nicht freigeschaltet" : ""
              }
            />
            <TextField
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              className={classes.input}
              variant="outlined"
              label="Passwort"
              type="password"
              disabled={loading}
            />
            <TextField
              value={klasse}
              onChange={(event) => setKlasse(event.target.value)}
              required
              className={classes.input}
              variant="outlined"
              label="Klasse"
              disabled={loading}
            />
            <Button
              type="submit"
              className={classes.loginBtn}
              variant="contained"
              color="primary"
              disabled={loading}
            >
              Account erstellen
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  return {
    props: {},
  };
};
