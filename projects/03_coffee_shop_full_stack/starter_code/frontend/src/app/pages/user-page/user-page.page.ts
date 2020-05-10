import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-user-page',
  templateUrl: './user-page.page.html',
  styleUrls: ['./user-page.page.scss'],
})
export class UserPagePage implements OnInit {
  loginURL: string;

  constructor(public auth: AuthService) {
    this.loginURL = auth.build_login_link('/tabs/user-page');
  }

  ngOnInit() {
  }

  logOut(){
    window.location.href = "https://my-fsnd-coffee-shop.auth0.com/v2/logout?returnTo=http%3A%2F%2Flocalhost%3A8100"
  }
}
