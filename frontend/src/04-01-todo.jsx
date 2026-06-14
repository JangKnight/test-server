import AuthReg from "./04-auth-reg";
import AuthData from "./04-auth-data";
import FetchData from "./04-fetch-data";

const TodoApp = ({ token, setToken, setAdminRefresh }) => {
  return (
    <section id="Todos" className="container h-dvh">
      <h2 className="text-2xl font-bold mb-4">Todo App</h2>
      <AuthReg onUserCreated={() => setAdminRefresh((c) => c + 1)} />
      <AuthData setToken={setToken} />
      <FetchData token={token} />
    </section>
  );
};

export default TodoApp;
