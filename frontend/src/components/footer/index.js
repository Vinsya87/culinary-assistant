import styles from "./style.module.css";
import { Container, LinkComponent } from "../index";

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <Container className={styles.footer__container}>
        <LinkComponent
          href="#"
          title="Ваш кулинарный друг"
          className={styles.footer__brand}
        />
        <div className={styles.footer__author}>
          <LinkComponent
            href="#"
            title="Автор"
            className={styles.footer__brand}
          />
          <div className={styles.social__main}>
            <a href="https://github.com/Vinsya87">
              <img className={styles.img__my} src="../github.png" alt="" />
            </a>
            <a href="https://t.me/Vinsya87">
              <img className={styles.img__my2} src="../telega-2.png" alt="" />
            </a>
          </div>
        </div>
      </Container>
    </footer>
  );
};

export default Footer;
