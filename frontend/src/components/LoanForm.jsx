import { useState } from "react";

const INITIAL_FORM = {
  applicant_name: "",
  Gender: "Male",
  Married: "Yes",
  Dependents: "0",
  Education: "Graduate",
  Self_Employed: "No",
  ApplicantIncome: "",
  CoapplicantIncome: "",
  LoanAmount: "",
  Loan_Amount_Term: "360",
  Credit_History: "1",
  Property_Area: "Urban",
};

export default function LoanForm({ onSubmit, loading }) {
  const [form, setForm] = useState(INITIAL_FORM);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...form,
      ApplicantIncome: Number(form.ApplicantIncome),
      CoapplicantIncome: Number(form.CoapplicantIncome),
      LoanAmount: Number(form.LoanAmount),
      Loan_Amount_Term: Number(form.Loan_Amount_Term),
      Credit_History: Number(form.Credit_History),
    });
  };

  const field = (label, name, type = "text", placeholder = "") => (
    <div className="field-group" key={name}>
      <label htmlFor={name}>{label}</label>
      <input
        id={name}
        name={name}
        type={type}
        value={form[name]}
        onChange={handleChange}
        placeholder={placeholder}
        required
      />
    </div>
  );

  const select = (label, name, options) => (
    <div className="field-group" key={name}>
      <label htmlFor={name}>{label}</label>
      <select id={name} name={name} value={form[name]} onChange={handleChange}>
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="loan-form">
      <h3 className="section-title">👤 Personal Details</h3>
      <div className="form-grid">
        {field("Full Name", "applicant_name", "text", "e.g. Ravi Kumar")}
        {select("Gender", "Gender", ["Male", "Female"])}
        {select("Married", "Married", ["Yes", "No"])}
        {select("Dependents", "Dependents", ["0", "1", "2", "3+"])}
        {select("Education", "Education", ["Graduate", "Not Graduate"])}
        {select("Self Employed", "Self_Employed", ["Yes", "No"])}
      </div>

      <h3 className="section-title">💰 Financial Details</h3>
      <div className="form-grid">
        {field("Applicant Income (₹)", "ApplicantIncome", "number", "e.g. 50000")}
        {field("Co-applicant Income (₹)", "CoapplicantIncome", "number", "e.g. 0")}
        {field("Loan Amount (₹ thousands)", "LoanAmount", "number", "e.g. 150")}
        {field("Loan Term (months)", "Loan_Amount_Term", "number", "e.g. 360")}
        {select("Credit History", "Credit_History", ["1", "0"])}
        {select("Property Area", "Property_Area", ["Urban", "Semiurban", "Rural"])}
      </div>

      <button
        id="predict-submit"
        type="submit"
        className="btn-primary btn-full"
        disabled={loading}
      >
        {loading ? <span className="spinner" /> : "🔍 Analyze Application"}
      </button>
    </form>
  );
}
