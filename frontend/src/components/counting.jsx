import { useState } from "react";

const CountComponent = () => {
  const [num, setNum] = useState(0);

  function incrementCount() {
    setNum((currentState) => {
      console.log(currentState + 1);
      return currentState + 1;
    });
  }

  return (
    <>
      <p>{num}</p>
      <button
        className="px-2 rounded-full bg-blue-500"
        type="button"
        onClick={incrementCount}
      >
        Click me!
      </button>
    </>
  );
};

export default CountComponent;
