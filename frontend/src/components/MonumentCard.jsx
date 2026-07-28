import { Link } from "react-router-dom";
import MonumentArt from "./MonumentArt";
import { MapPin, ArrowRight } from "./Icon";
import "./MonumentCard.css";

export default function MonumentCard({ landmark }) {
  const { id, name, name_urdu, description, short_description, period, built_by } = landmark;
  const blurb = short_description || description || `${built_by ? `Built by ${built_by}` : "A landmark"}${period ? ` during the ${period} period.` : "."}`;

  return (
    <Link to={`/monument/${id}`} className="m-card card card-hover">
      <MonumentArt id={id} name={name} src={landmark.image_url || landmark.image} rounded="0" topOnly aspect="4 / 3" />
      <div className="m-card-body">
        <div className="m-card-top">
          <h3 className="m-card-name">{name}</h3>
          {name_urdu && <span className="m-card-urdu">{name_urdu}</span>}
        </div>
        <p className="m-card-desc">{blurb}</p>
        <div className="m-card-footer">
          <span className="m-card-loc"><MapPin size={14} /> Lahore Fort</span>
          <span className="m-card-link">Learn More <ArrowRight size={14} /></span>
        </div>
      </div>
    </Link>
  );
}
