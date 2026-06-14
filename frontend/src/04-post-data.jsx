import { analytics } from "./lib/ingest";

const PostData = ({ setTodos, token }) => {
  const postData = async (form) => {
    form.preventDefault();

    const formData = new FormData(form.target);
    const newTodo = {
      title: formData.get("title"),
      description: formData.get("description") || null,
      priority: parseInt(formData.get("priority")),
      completed: false,
    };

    const url = "/api/todos";

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(newTodo),
    });
    if (res.ok) {
      analytics.track("todo_created", { priority: 2 });
      const updatedTodos = await res.json();
      setTodos(updatedTodos);
      form.target.reset();
    }
  };
  return (
    <>
      {/*
        Form that matches the following Pydantic model in the backend:
        def __init__(self, title: str, description: str = None, priority: int = 1, completed: bool = False):
            self.title = title
            self.description = description
            self.priority = priority
            self.completed = completed
        */}

      <form className="mt-1 mb-5" onSubmit={postData}>
        <input type="text" name="title" placeholder="title" />
        <input type="text" name="description" placeholder="description" />
        <input type="number" name="priority" placeholder="priority" />
        <button className="mx-3 btn btn-primary" type="submit">
          Submit
        </button>
      </form>
    </>
  );
};

export default PostData;
