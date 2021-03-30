import axios from "axios";
import { Post } from "./types";

if (process.browser) {
  axios.defaults.baseURL = `http://${window.location.hostname}:5000/`;
} else {
  axios.defaults.baseURL = `http://localhost:5000/`;
}

export async function loginpermanent(username: string, password: string) {
  return (await axios.post("loginpermanent", { username, password })).data.data
    .token;
}

export async function getPosts(
  token: string,
  channel: string,
  amount: number,
  lastId?: number
): Promise<Post[]> {
  return (
    await axios.get(`posts/${channel}/${amount}/${lastId ? lastId : 0}`, {
      auth: {
        username: token,
        password: "unused",
      },
    })
  ).data.data as Post[];
}

export async function getChannelNames(
  token: string,
  name: string
): Promise<string[]> {
  if (name == "") return [];
  return (
    await axios.get(`channels/name/${name}`, {
      auth: {
        username: token,
        password: "unused",
      },
    })
  ).data.data;
}

export async function createPost(
  token: string,
  channel: string,
  title: string,
  text?: string,
  file?: string
) {
  axios.post(
    `posts/${channel}/create`,
    {
      title,
      text: text ? text : "",
      ...(file ? { file } : {}),
    },
    {
      auth: {
        username: token,
        password: "unused",
      },
    }
  );
}

export async function createUser(
  username: string,
  password: string,
  classname: string
) {
  await axios.post("users/create", { username, password, classname });
  return loginpermanent(username, password);
}
