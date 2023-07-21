// import React from 'react';
import { useEffect, useState, useRef } from "react";
import logo from './logo.svg';
import './App.css';
import SortableTable from "./components/SortableTable";
import PatientInfoForm from "./components/PatientInfoForm";
import GeneButton from "./components/GeneButton";
import { ListFormat } from "typescript";
import axios from "axios";

const data = [{ 'id': 1234, 'molecular_impact': 'HIGH', 'pathogenicity': 'benign' },
{ 'id': 2345, 'molecular_impact': '', 'pathogenicity': 'likely pathogenic' },
{ 'id': 3456, 'molecular_impact': 'LOW', 'pathogenicity': 'benign' },
{ 'id': 4567, 'molecular_impact': 'MED', 'pathogenicity': 'benign' },];

type VariantRow = {
  spdi: string,
  dnaChangeType: string,
  sourceClass: string,
  allelicState: string,
  molecImpact: string,
  alleleFreq: number,
}

function App() {
  const [geneButtons, setGeneButtons] = useState<Array<{ geneName: string, geneData: Array<VariantRow> }>>([])
  const [selectedGene, setSelectedGene] = useState<{ geneName: string, geneData: Array<VariantRow> }>({ geneName: "None", geneData: [] })

  var geneListData: Array<{ geneName: string, geneData?: Array<VariantRow> }> = []

  // const handleForm = (formData: { patientID: string, geneList: Array<string>, addAnnFlag: boolean }) => {
  //   // Update these state variables from within the form component
  //   patientID.current = formData.patientID
  //   setGeneList(formData.geneList)
  //   addAnnFlag.current = formData.addAnnFlag

  // }

  const getGeneData = (newGene: { geneName: string, geneData: Array<VariantRow> }) => {
    // Update state variable from within the form component
    setGeneButtons((prevGeneButtons) => {
      let geneButtonsUpdatedTarget = prevGeneButtons.filter(function (geneDict) {
        return geneDict.geneName !== newGene.geneName
      })

      geneButtonsUpdatedTarget.push(newGene)

      console.log("In get gene data for gene ", newGene.geneName)
      console.log("geneButtons is ", geneButtons)
      console.log("geneButtons Updated target is", geneButtonsUpdatedTarget)

      return geneButtonsUpdatedTarget
    })

  }

  function makeButton(geneDict: { geneName: string, geneData: Array<VariantRow> }) {
    if (geneDict.geneName == "BRCA1") {
      console.log(geneButtons)
    }
    return (
      <button
        style={{ color: 'green' }}
        onClick={() => setSelectedGene(geneDict)}>
        {geneDict.geneName}
      </button>
    );
  }

  return (
    <div className="App">
      <div id="patientInfoForm">
        <PatientInfoForm callback={getGeneData} />
      </div>
      <div>
        {geneButtons.map((geneDict) => makeButton(geneDict))}
      </div>
      <p>Gene Displayed: {selectedGene.geneName}</p>
      <SortableTable data={selectedGene.geneData} />
    </div>
  );
}

export default App;
