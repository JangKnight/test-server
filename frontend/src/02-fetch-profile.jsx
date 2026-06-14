import { useEffect, useState } from "react";
import { analytics } from "./lib/ingest";

const FetchProfile = () => {
  const [username, setUsername] = useState("JangKnight");
  const [profile, setProfile] = useState(null);

  const changeUser = (form) => {
    form.preventDefault();
    const formData = new FormData(form.target);
    let username = formData.get("username");
    setUsername(username.trim() || "JangKnight");
    form.target.reset();
  };

  const fetchProfile = async () => {
    try {
      analytics.track("button_clicked", { priority: 2 });
      const res = await fetch(`https://api.github.com/users/${username}`);
      analytics.track("profile_fetched", { priority: 2 });
      if (res.ok) {
        const data = await res.json();
        console.log(data);
        setProfile(data);
      } else {
        analytics.track("profile_fetch_error", {
          priority: 2,
          status: res.status,
        });
        console.error("Error fetching profile:", res.status);
      }
    } catch (error) {
      analytics.track("profile_fetch_error", {
        priority: 2,
        error: error.message,
      });
      console.error("Network error:", error);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [username]);
  return (
    <section id="Home" className="h-dvh container">
      <h2>{profile ? `${profile.login}'s Profile` : "Fetch GH Profile"}</h2>
      <form onSubmit={changeUser}>
        <input type="text" name="username" placeholder="GitHub username" />
        <button className="mx-3 btn btn-primary" type="submit">
          Fetch Profile
        </button>
      </form>

      {profile && (
        <div>
          <a
            href={profile.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-24 h-24 rounded-full mb-4 mx-auto block"
          >
            <img
              src={profile.avatar_url}
              alt={`${profile.login}'s avatar`}
              className="w-24 h-24 rounded-full mb-4 mx-auto"
            />
          </a>

          <p>Name: {profile.name}</p>
          <p>Bio: {profile.bio}</p>
          <p>Location: {profile.location}</p>
        </div>
      )}
    </section>
  );
};
export default FetchProfile;
