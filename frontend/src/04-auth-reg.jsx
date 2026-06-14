{
  /*
                  sign up form capable of producing basic oauth2 reqs similar to this https post request:
                  {
                    "email": "test1@example.com",
                    "username": "testuser1",
                    "password": "password123",
                    "first_name": "Test",
                    "last_name": "User",
                  }
    */
}

import { useState } from "react";
import { analytics } from "./lib/ingest";

const url = "/api/auth";

const AuthReg = ({ onUserCreated }) => {
  const [message, setMessage] = useState("");
  const postData = async (form) => {
    form.preventDefault();

    const formData = new FormData(form.target);
    const data = {
      email: formData.get("email"),
      username: formData.get("username"),
      password: formData.get("password"),
      first_name: formData.get("first_name"),
      last_name: formData.get("last_name"),
    };

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(data),
    });

    if (res.ok) {
      analytics.track("user_created", { priority: 1 });
      setMessage("User created successfully!");
      form.target.reset();
      onUserCreated?.();
      setTimeout(() => setMessage(""), 1000);
    } else {
      setMessage("Error creating user.");
    }
  };

  return (
    <>
      <form className="mt-1 mb-5" onSubmit={postData}>
        <input type="email" name="email" placeholder="email" />
        <input type="text" name="username" placeholder="username" />
        <input type="password" name="password" placeholder="password" />
        <input type="text" name="first_name" placeholder="first name" />
        <input type="text" name="last_name" placeholder="last name" />
        <button className="mx-3 btn btn-primary" type="submit">
          Sign Up
        </button>
      </form>
      {message && <p>{message}</p>}
    </>
  );
};

export default AuthReg;
