import { useState } from "react";
import Nav from "./01-header-nav";
import TodoApp from "./04-01-todo";
import Note from "./01-quick-note";
import FetchProfile from "./02-fetch-profile";
import FetchAdmin from "./03-admin-rule";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [adminRefresh, setAdminRefresh] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div>
      <Nav />
      <Note />
      <FetchProfile />
      <TodoApp
        token={token}
        setToken={setToken}
        setAdminRefresh={setAdminRefresh}
      />
      <FetchAdmin token={token} refreshKey={adminRefresh} />
    </div>
  );
}

export default App;
