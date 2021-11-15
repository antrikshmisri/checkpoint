import React from "react";

import { Container } from "react-bootstrap";
import FolderTree from "react-folder-tree";
import "bootstrap/dist/css/bootstrap.min.css";

const Tree = ({ structure }) => {
  const visitedFolders = [];
  const treeStructure = {
    name: Object.keys(structure)[0],
    isOpen: false,
    children: [
      ...Object.keys(structure)
        .slice(1, structure.length)
        .flatMap((key) => {
          if (!visitedFolders.includes(key)) {
            visitedFolders.push(key);
            return {
              name: key,

              isOpen: false,
              children: [
                ...structure[key].files.map((item) => {
                  return {
                    name: item,
                  };
                }),
                ...structure[key].folders.map((item) => {
                  visitedFolders.push(item);
                  return {
                    name: item,

                    isOpen: false,
                    children: [
                      ...structure[item].files.map((item) => {
                        return {
                          name: item,
                        };
                      }),
                    ],
                  };
                }),
              ],
            };
          }
        })
        .filter((item) => item !== undefined),
      ...structure[Object.keys(structure)[0]].files.map((item) => {
        return {
          name: item,
        };
      }),
    ],
  };
  return (
    <Container className="tree-root fluid">
      <FolderTree
        showCheckbox={false}
        data={treeStructure}
        readOnly
        indentPixels={20}
      />
    </Container>
  );
};

export default Tree;
