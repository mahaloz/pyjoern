/* This code only exists to attempt to confuse pyjoern by having two files
 * with a function called ngx_mail_pop3_init_session. AND a declaration of it.
 */
void ngx_mail_pop3_init_session(ngx_mail_session_t *s, ngx_connection_t *c);

void
ngx_mail_pop3_init_session(ngx_mail_session_t *s, ngx_connection_t *c)
{
    u_char                    *p;
    ngx_mail_core_srv_conf_t  *cscf;
    ngx_mail_pop3_srv_conf_t  *pscf;

    pscf = ngx_mail_get_module_srv_conf(s, ngx_mail_pop3_module);
    cscf = ngx_mail_get_module_srv_conf(s, ngx_mail_core_module);

    if (pscf->auth_methods
        & (NGX_MAIL_AUTH_APOP_ENABLED|NGX_MAIL_AUTH_CRAM_MD5_ENABLED))
    {
        if (ngx_mail_salt(s, c, cscf) != NGX_OK) {
            ngx_mail_session_internal_server_error(s);
            return;
        }

        s->out.data = ngx_pnalloc(c->pool, sizeof(pop3_greeting) + s->salt.len);
        if (s->out.data == NULL) {
            ngx_mail_session_internal_server_error(s);
            return;
        }

        p = ngx_cpymem(s->out.data, pop3_greeting, sizeof(pop3_greeting) - 3);
        *p++ = ' ';
        p = ngx_cpymem(p, s->salt.data, s->salt.len);

        s->out.len = p - s->out.data;

    } else {
        ngx_str_set(&s->out, pop3_greeting);
    }

    c->read->handler = ngx_mail_pop3_init_protocol;

    ngx_add_timer(c->read, cscf->timeout);

    if (ngx_handle_read_event(c->read, 0) != NGX_OK) {
        ngx_mail_close_connection(c);
    }

    ngx_mail_send(c->write);
}