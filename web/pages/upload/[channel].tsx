import {
  Button,
  Card,
  CardContent,
  CardMedia,
  Input,
  LinearProgress,
  TextField,
  Typography,
} from "@material-ui/core";
import Cookies from "js-cookie";
import { createPost } from "lib/api";
import { GetServerSideProps } from "next";
import { useRouter } from "next/dist/client/router";
import { useState } from "react";

export default function Upload({ channel }) {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [image, setImage] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  return (
    <div>
      <Card style={{ maxWidth: 500, margin: "auto", marginTop: 50 }}>
        {image && (
          <CardMedia>
            <img
              style={{ width: "100%", height: 200, objectFit: "cover" }}
              src={`data:image;base64,${image}`}
            />
          </CardMedia>
        )}
        <CardContent>
          <Typography variant="h5">Upload</Typography>
          <form
            className="form"
            onSubmit={(event) => {
              event.preventDefault();
              setLoading(true);
              createPost(
                Cookies.get("token"),
                channel,
                title,
                text,
                image
              ).then(() => {
                router.push(`/posts/${channel}`);
              });
            }}
          >
            <TextField
              disabled={loading}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              required
              label="Titel"
            />
            <TextField
              disabled={loading}
              value={text}
              onChange={(event) => setText(event.target.value)}
              label="Text"
              multiline
            />
            <input
              disabled={loading}
              className="fileInp"
              type="file"
              accept="image/png,image/jpeg"
              onChange={(event) => {
                const reader = new FileReader();
                reader.onload = () => {
                  setImage(reader.result.toString().split(",").pop());
                };
                reader.readAsDataURL(event.target.files[0]);
              }}
            />
            <Button type="submit" color="primary" disabled={loading}>
              Upload
            </Button>
          </form>
        </CardContent>
        <LinearProgress style={{ opacity: loading ? 1 : 0 }} />
      </Card>
      <style jsx>{`
        .form {
          display: flex;
          flex-direction: column;
        }

        .form > :global(div) {
          margin-top: 20px;
        }

        .fileInp {
          margin-top: 20px;
          margin-bottom: 20px;
        }
      `}</style>
    </div>
  );
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  if (!context.req.cookies.token)
    return {
      redirect: {
        statusCode: 303,
        destination: "/login",
      },
    };
  return {
    props: {
      channel: context.params.channel.toString(),
    },
  };
};
