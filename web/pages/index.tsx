import { Button } from "@material-ui/core";
import ChannelSearch from "components/channelSearch";
import { GetServerSideProps } from "next";

export default function Home() {
  return (
    <div className="container">
      <div className="search">
        <ChannelSearch />
      </div>
      <style jsx>{`
        .container {
          display: flex;
          flex-direction: column;
        }

        .search {
          margin-top: 20px;
          width: 300px;
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
    props: {},
  };
};
