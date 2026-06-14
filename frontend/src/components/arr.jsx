import { data } from "../data";
import React from "react";

const Arr = () => {
  const [people, setPeople] = React.useState(data);

  return (
    <>
      {people.map((person) => {
        console.log(person);
        return (
          <div key={person.id}>
            <h6 className="m-2 inline-block">
              {person.name.charAt(0).toUpperCase() + person.name.slice(1)}
            </h6>
            <button
              className=" px-2 rounded-full bg-red-500"
              onClick={() =>
                setPeople(people.filter((p) => p.id !== person.id))
              }
            >
              Remove
            </button>
            <br />
          </div>
        );
      })}
      <button
        className="px-2 mt-10 rounded-full bg-red-500"
        type="button"
        onClick={() => setPeople([])}
      >
        Clear
      </button>
    </>
  );
};

export default Arr;
