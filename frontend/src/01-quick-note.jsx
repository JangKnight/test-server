import { useEffect, useState } from "react";

const Note = () => {
  return (
    <section
      id="Note"
      className="h-dvh container flex flex-col items-center justify-center text-center"
    >
      <p className="text-2xl font-bold mb-4">Thanks for dropping by!</p>
      <p>
        This is just my sandbox site where I experiment with different security,
        development, and deployment concepts using docker and a VPS.
      </p>
      <p>
        You may be interested in my{" "}
        <a
          className="text-indigo-400 hover:text-indigo-800"
          href="https://dev.anthonysjhenry.com"
        >
          portfolio page
        </a>
        .
      </p>
    </section>
  );
};
export default Note;
