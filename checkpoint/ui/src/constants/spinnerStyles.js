import { css } from "@emotion/react";

const spinnerStyle = css`
  z-index: 10;
  position: absolute;
  size: 100px;
  top: calc(50% - 37.5px);
  left: calc(50% - 37.5px);
  border-radius: 50%;
  width: 75px;
  height: 75px;
  transform: rotate(45deg);
`;

export default spinnerStyle;
