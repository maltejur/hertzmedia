import { Button, Link, Typography } from "@material-ui/core";
import NextLink from "next/link";
import Cookies from "js-cookie";
import { useRouter } from "next/dist/client/router";

export default function Layout({ children }) {
  const router = useRouter();

  return (
    <div className="container">
      <div className="navbar">
        <NextLink href="/" passHref>
          <Link color="textPrimary">
            <Typography variant="h2">hertzmedia</Typography>
          </Link>
        </NextLink>
        {Cookies.get("token") && (
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              Cookies.remove("token");
              router.push("/");
            }}
          >
            Logout
          </Button>
        )}
      </div>
      {children}
      <style jsx>{`
        .container {
          max-width: 1000px;
          margin: auto;
          padding: 20px;
        }

        .navbar {
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
        }
      `}</style>
    </div>
  );
}
