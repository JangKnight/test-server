import { useState, useEffect } from "react";
import PostData from "./04-post-data";
const url = "/api/";

const FetchData = ({ token }) => {
  const [todos, setTodos] = useState([]);

  const deleteData = async (id) => {
    const res = await fetch(`/api/todos/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      method: "DELETE",
    });
    if (res.ok) {
      const updatedTodos = await res.json();
      setTodos(updatedTodos);
    }
  };

  const fetchTodos = async () => {
    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      method: "GET",
    });
    const todos = await res.json();
    console.log(todos);
    setTodos(todos);
  };

  useEffect(() => {
    fetchTodos();
  }, [token]);

  if (!Array.isArray(todos)) {
    return (
      <>
        <PostData token={token} />
        <p>Log in to view your todos.</p>
      </>
    );
  }

  return (
    <>
      <PostData setTodos={setTodos} token={token} />
      {todos.map((todo) => (
        <div
          key={todo.id}
          className="flex items-center justify-between p-2 mb-2 bg-gray-100 rounded group"
        >
          <span>{todo.title}</span>

          <button
            onClick={() => deleteData(todo.id)}
            className="text-red-500 hover:text-red-700 font-bold px-2 cursor-pointer transition-colors"
            title="Delete Todo"
          >
            ✕
          </button>
        </div>
      ))}
    </>
  );
};
export default FetchData;
