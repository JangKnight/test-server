import { useState, useEffect } from "react";
import { analytics } from "./lib/ingest";

const url = "/api/auth/token";

const AuthData = ({ setToken }) => {
  const [message, setMessage] = useState("");
  const postData = async (form) => {
    form.preventDefault();

    const formData = new FormData(form.target);
    const data = {
      username: formData.get("username"),
      password: formData.get("password"),
    };

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(data),
    });
    if (res.ok) {
      const responseData = await res.json();
      setToken(responseData.access_token);
      setMessage("Logged in successfully.");
      setTimeout(() => setMessage(""), 1000);
      localStorage.setItem("token", responseData.access_token);
      form.target.reset();
    } else {
      setMessage("Error logging in.");
      setTimeout(() => setMessage(""), 1000);
    }
  };

  return (
    <>
      <form className="mt-1 mb-5" onSubmit={postData}>
        <input type="text" name="username" placeholder="username" />
        <input type="password" name="password" placeholder="password" />
        <button className="mx-3 btn btn-primary" type="submit">
          Login
        </button>
        <button
          className="mx-3 btn btn-secondary"
          type="button"
          onClick={() => {
            setToken(null);
            setMessage("Logged out.");
            localStorage.removeItem("token");
            setTimeout(() => setMessage(""), 1000);
          }}
        >
          Logout
        </button>
      </form>
      {message && message === "Error logging in." ? (
        <p className="text-red-500">{message}</p>
      ) : (
        <p className="text-green-500">{message}</p>
      )}
    </>
  );
};

export default AuthData;
