import {
  Avatar,
  Card,
  CardContent,
  CardHeader,
  CardMedia,
  CircularProgress,
  Fab,
  Typography,
} from "@material-ui/core";
import { Add } from "@material-ui/icons";
import Cookies from "js-cookie";
import { getPosts } from "lib/api";
import { Post } from "lib/types";
import { GetServerSideProps } from "next";
import NextLink from "next/link";
import { useEffect, useState } from "react";
import { format as timeago } from "timeago.js";
import { titleCase } from "title-case";

export default function Posts({
  initialPosts,
  channel,
}: {
  initialPosts: Post[];
  channel: string;
}) {
  const [posts, setPosts] = useState(initialPosts);
  const [loading, setLoading] = useState(false);
  const [atBottom, setAtBottom] = useState(false);

  function tryAddNewPosts() {
    if (
      document.body.scrollHeight - window.innerHeight - window.scrollY < 200 &&
      !loading &&
      !atBottom
    ) {
      setLoading(true);
      getPosts(
        Cookies.get("token"),
        channel,
        10,
        posts[posts.length - 1].id
      ).then((newPosts) => {
        if (newPosts.length === 0) {
          setAtBottom(true);
        }
        setPosts((posts) => [...posts, ...newPosts]);
        setLoading(false);
      });
    }
  }

  useEffect(() => {
    console.log(atob(initialPosts[0].file));
    window.addEventListener("scroll", tryAddNewPosts);
    return () => window.removeEventListener("scroll", tryAddNewPosts);
  });

  return (
    <div className="container">
      <Typography variant="h4" style={{ marginTop: 30, marginBottom: 20 }}>
        {channel}
      </Typography>
      <div className="posts">
        {posts.map((post) => (
          <Card key={post.id}>
            {post.file && (
              <CardMedia>
                <img className="image" src={`data:image;base64,${post.file}`} />
              </CardMedia>
            )}
            <CardHeader
              avatar={<Avatar>{post.creator[0].toUpperCase()}</Avatar>}
              title={titleCase(post.creator)}
              subheader={timeago(new Date(post.time))}
            />
            <CardContent>
              <Typography variant="h5">{post.title}</Typography>
              {post.text && <Typography>{post.text}</Typography>}
            </CardContent>
          </Card>
        ))}
        {loading && (
          <CircularProgress style={{ alignSelf: "center" }} size="30px" />
        )}
      </div>
      <NextLink href={`/upload/${channel}`} passHref>
        <Fab
          style={{ position: "fixed", right: 30, bottom: 30 }}
          color="primary"
        >
          <Add />
        </Fab>
      </NextLink>
      <style jsx>{`
        .container {
          width: 500px;
          max-width: 100%;
          margin: auto;
        }

        .posts {
          display: flex;
          flex-direction: column;
        }

        .posts > :global(div) {
          margin-bottom: 40px;
        }

        .image {
          max-height: 500px;
          width: 100%;
          object-fit: cover;
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
      initialPosts: await getPosts(
        context.req.cookies.token,
        context.params.channel.toString(),
        100
      ),
      channel: context.params.channel.toString(),
    },
  };
};
