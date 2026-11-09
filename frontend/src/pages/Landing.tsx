import { Link } from 'react-router'

export default function Landing() {
  return (
    <section className="hero">
      <h1>Conversations your students can play through</h1>
      <p>Create a dialogue scenario with a character, a setting and goals. Students practice by talking it through.</p>
      <Link to="/create" className="btn btn-primary btn-large">
        Get started
      </Link>
    </section>
  )
}
