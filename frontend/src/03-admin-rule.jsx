import { useState, useEffect } from "react";

const FetchAdmin = ({ token, refreshKey }) => {
  const [userList, setUserList] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);

  const deleteData = async (id) => {
    const res = await fetch(`/api/admin/users/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (res.ok) {
      fetchAdmin();
    } else {
      console.error("Error deleting user:", res.status);
    }
  };

  const fetchAdmin = async () => {
    try {
      const res = await fetch(`/api/admin/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      });
      if (res.ok) {
        const data = await res.json();
        console.log(data);
        setUserList(data);
        setIsAdmin(true);
      } else {
        console.error("Error fetching user list:", res.status);
        setUserList([]);
        setIsAdmin(false);
      }
    } catch (error) {
      console.error("Network error:", error);
      setUserList([]);
      setIsAdmin(false);
    }
  };

  useEffect(() => {
    fetchAdmin();
  }, [token, refreshKey]);

  let content = "";
  if (!isAdmin) {
    content = <p>Please log in as admin to view admin content.</p>;
  } else {
    content = (
      <>
        <h2>All Users</h2>
        <ul>
          {userList.map((user) => (
            <li key={user.id}>
              {user.username} - {user.email}
              <button
                onClick={() => deleteData(user.id)}
                className="text-red-500 hover:text-red-700 font-bold px-2 cursor-pointer transition-colors"
                title="Delete User"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      </>
    );
  }

  return (
    <section id="Admin" className="h-dvh container">
      {content}
    </section>
  );
};

export default FetchAdmin;
